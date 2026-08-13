import io
import streamlit as st
import pandas as pd
from database.db import get_db
from database import models
from utils.material_calculator import BUILDING_TYPES, estimate_materials
from utils.styling import page_hero, stat_card


def _get_project_id() -> int | None:
    with get_db() as conn:
        project = models.get_default_project(conn)
        return int(project["id"]) if project else None


def _boq_to_csv(boq_rows: list[dict]) -> bytes:
    df = pd.DataFrame(boq_rows)
    return df.to_csv(index=False).encode("utf-8")


def render():
    page_hero(
        "🧱", "AI Material Estimation",
        "Material quantities, cost, labour, equipment &amp; BOQ generation with waste allowance (in Indian Rupees ₹)",
        badge="QUANTITY SURVEYING — INDIA"
    )

    st.markdown("""
        <div class="hub-card" style="margin-bottom: 18px; padding: 16px 20px;">
            <h4>📐 Project Specifications</h4>
            <span class="hub-card-tag">Enter dimensions &amp; building parameters to generate a full Bill of Quantities</span>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        area = st.number_input("Built-up Area (sq ft)", min_value=100, value=2500, step=100, key="mat_area")
        floors = st.number_input("Number of Floors", min_value=1, value=2, step=1, key="mat_floors")

    with col2:
        building_type = st.selectbox("Building Type", list(BUILDING_TYPES.keys()), key="mat_btype")
        duration = st.number_input("Duration (days)", min_value=30, value=90, step=5, key="mat_duration")

    with col3:
        waste_buffer = st.slider("Extra Waste Buffer (%)", 0, 15, 0, help="Additional waste on top of standard allowances", key="mat_waste")
        include_save = st.checkbox("Auto-save BOQ on calculation", value=False, key="mat_autosave")

    st.markdown("<br>", unsafe_allow_html=True)

    # Trigger generation or check session state
    generate_clicked = st.button("📊 Generate Material Estimate & BOQ", type="primary", use_container_width=True)

    if generate_clicked or "material_result" not in st.session_state:
        try:
            res = estimate_materials(area, floors, building_type, duration)
            if waste_buffer > 0:
                for mat in res.materials:
                    mat.waste_pct += waste_buffer
            st.session_state["material_result"] = res
            st.session_state["material_params"] = (area, floors, building_type, duration, waste_buffer)
        except Exception as exc:
            st.error(f"Error calculating materials: {exc}")

    result = st.session_state.get("material_result")

    if result:
        st.markdown("<hr class='hub-divider'>", unsafe_allow_html=True)

        # Summary KPIs in Indian Rupees (₹)
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(stat_card("🧱", "Material Cost", f"₹{result.material_cost:,.0f}", None, "#00E5FF"), unsafe_allow_html=True)
        with k2:
            st.markdown(stat_card("👷", "Labour Cost", f"₹{result.labour_cost:,.0f}", None, "#7C3AED"), unsafe_allow_html=True)
        with k3:
            st.markdown(stat_card("🚜", "Equipment Cost", f"₹{result.equipment_cost:,.0f}", None, "#FF2E93"), unsafe_allow_html=True)
        with k4:
            st.markdown(stat_card("💰", "Total BOQ Cost", f"₹{result.total_cost:,.0f}", f"Waste: ₹{result.total_waste_cost:,.0f}", "#00E676"), unsafe_allow_html=True)

        tab_mat, tab_lab, tab_eq, tab_boq = st.tabs(["🧱 Materials", "👷 Labour", "🚜 Equipment", "📋 Full BOQ"])

        with tab_mat:
            mat_rows = [
                {
                    "Material": m.material,
                    "Quantity": round(m.quantity, 2),
                    "Unit": m.unit,
                    "Waste %": f"{m.waste_pct:.1f}%",
                    "Gross Qty": round(m.gross_quantity, 2),
                    "Unit Cost (₹)": f"₹{m.unit_cost:,.2f}",
                    "Total (₹)": f"₹{m.total_cost:,.2f}",
                }
                for m in result.materials
            ]
            st.dataframe(pd.DataFrame(mat_rows), use_container_width=True, hide_index=True)

        with tab_lab:
            lab_rows = [
                {
                    "Trade": row["trade"],
                    "Workers": row["workers"],
                    "Man Days": row["man_days"],
                    "Daily Rate (₹)": f"₹{row['daily_rate']:,.2f}",
                    "Total Cost (₹)": f"₹{row['total_cost']:,.2f}",
                }
                for row in result.labour
            ]
            st.dataframe(pd.DataFrame(lab_rows), use_container_width=True, hide_index=True)

        with tab_eq:
            eq_rows = [
                {
                    "Equipment": row["equipment"],
                    "Days": row["days"],
                    "Daily Rate (₹)": f"₹{row['daily_rate']:,.2f}",
                    "Total Cost (₹)": f"₹{row['total_cost']:,.2f}",
                }
                for row in result.equipment
            ]
            st.dataframe(pd.DataFrame(eq_rows), use_container_width=True, hide_index=True)

        with tab_boq:
            boq_rows = result.boq_rows()
            st.dataframe(pd.DataFrame(boq_rows), use_container_width=True, hide_index=True)

            b_col1, b_col2 = st.columns(2)
            with b_col1:
                csv_data = _boq_to_csv(boq_rows)
                st.download_button(
                    "📥 Download BOQ (CSV)",
                    data=csv_data,
                    file_name=f"boq_{building_type.lower()}_{area}sqft.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            with b_col2:
                project_id = _get_project_id()
                if project_id and st.button("💾 Save BOQ to Database", type="primary", use_container_width=True, key="save_boq_db"):
                    try:
                        with get_db() as conn:
                            for row in boq_rows:
                                models.create_material_record(
                                    conn,
                                    project_id=project_id,
                                    category=str(row.get("Category", "Material")),
                                    item=str(row.get("Item", "")),
                                    quantity=float(row.get("Quantity", 0)),
                                    unit=str(row.get("Unit", "")),
                                    unit_rate=float(row.get("Unit Rate (₹)", 0)),
                                    amount=float(row.get("Amount (₹)", 0)),
                                )
                        st.success(f"✅ BOQ saved successfully to SQLite database ({len(boq_rows)} items stored).")
                    except Exception as exc:
                        st.error(f"⚠️ Failed to save BOQ: {exc}")

    # Existing saved material records
    project_id = _get_project_id()
    if project_id:
        with get_db() as conn:
            existing = models.list_material_records(conn, project_id, limit=25)
            summary = models.get_material_cost_summary(conn, project_id)
        if existing:
            st.markdown("<hr class='hub-divider'>", unsafe_allow_html=True)
            st.markdown(f"<h4 style='color: #00E5FF;'>📋 Saved Material Records History — Total: ₹{summary['total_cost']:,.2f}</h4>", unsafe_allow_html=True)
            st.dataframe(
                pd.DataFrame([
                    {
                        "Material / Item": r["material"],
                        "Qty": r["quantity"],
                        "Unit": r["unit"],
                        "Unit Cost (₹)": f"₹{r['unit_cost']:,.2f}",
                        "Waste %": f"{r['waste_pct']}%",
                    }
                    for r in existing
                ]),
                use_container_width=True,
                hide_index=True,
            )
