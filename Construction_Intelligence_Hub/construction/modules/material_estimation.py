import streamlit as st
import pandas as pd
from utils.material_calculator import estimate_materials, DEFAULT_UNIT_RATES
from utils.llama_client import chat_with_llama


def render():
    st.markdown(
        """<div class="page-header">
        <h1>🧱 Material Estimation (AI)</h1>
        <p>Enter the built-up area — get an instant AI-assisted material & cost estimate.</p>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="cih-card">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        area_sqft = st.number_input("Built-up Area (sq.ft)", min_value=1.0, step=50.0, value=1000.0)
    with col2:
        floors = st.number_input("Number of Floors", min_value=1, step=1, value=1)
    with col3:
        tier = st.selectbox("Quality Tier", ["Economy", "Standard", "Premium"], index=1)

    with st.expander("⚙️ Advanced: edit unit rates (INR)"):
        rate_cols = st.columns(4)
        keys = list(DEFAULT_UNIT_RATES.keys())
        custom_rates = {}
        for i, k in enumerate(keys):
            with rate_cols[i % 4]:
                custom_rates[k] = st.number_input(f"{k.capitalize()} rate", value=float(DEFAULT_UNIT_RATES[k]), key=f"rate_{k}")

    run = st.button("🔮 Generate AI Estimate")
    st.markdown("</div>", unsafe_allow_html=True)

    if run:
        result = estimate_materials(area_sqft, tier=tier, floors=floors, unit_rates=custom_rates)

        st.markdown('<div class="cih-card">', unsafe_allow_html=True)
        st.subheader(f"📦 Estimated Materials for {result.area_sqft:.0f} sq.ft ({tier} tier)")

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-tile"><div class="value">{result.cement_bags}</div><div class="label">Cement (bags)</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-tile"><div class="value">{result.steel_kg}</div><div class="label">Steel (kg)</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-tile"><div class="value">{result.sand_cft}</div><div class="label">Sand (cft)</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="metric-tile"><div class="value">{result.aggregate_cft}</div><div class="label">Aggregate (cft)</div></div>', unsafe_allow_html=True)

        m5, m6, m7, m8 = st.columns(4)
        with m5:
            st.markdown(f'<div class="metric-tile"><div class="value">{result.bricks_nos:.0f}</div><div class="label">Bricks (nos)</div></div>', unsafe_allow_html=True)
        with m6:
            st.markdown(f'<div class="metric-tile"><div class="value">{result.paint_litres}</div><div class="label">Paint (L)</div></div>', unsafe_allow_html=True)
        with m7:
            st.markdown(f'<div class="metric-tile"><div class="value">{result.tiles_sqft:.0f}</div><div class="label">Tiles (sq.ft)</div></div>', unsafe_allow_html=True)
        with m8:
            st.markdown(f'<div class="metric-tile"><div class="value">{result.labour_mandays:.0f}</div><div class="label">Labour (man-days)</div></div>', unsafe_allow_html=True)

        st.markdown("<div class='cih-divider'></div>", unsafe_allow_html=True)

        cost_df = pd.DataFrame(
            [{"Material": k.capitalize(), "Cost (INR)": v} for k, v in result.cost_breakdown.items()]
        )
        cc1, cc2 = st.columns([1.3, 1])
        with cc1:
            st.dataframe(cost_df, use_container_width=True, hide_index=True)
        with cc2:
            st.bar_chart(cost_df.set_index("Material"))

        st.markdown(
            f'<div class="metric-tile" style="margin-top:14px;"><div class="value">₹ {result.total_cost:,.0f}</div>'
            f'<div class="label">Estimated Total Material Cost</div></div>',
            unsafe_allow_html=True,
        )
        st.caption("⚠️ These are approximate thumb-rule estimates for early budgeting. Always confirm final BOQ with a structural engineer / quantity surveyor.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="cih-card">', unsafe_allow_html=True)
        st.subheader("🤖 Ask Llama to explain this estimate")
        if st.button("Get AI Explanation"):
            with st.spinner("Thinking..."):
                prompt = (
                    f"A client has a {result.area_sqft:.0f} sq.ft {tier.lower()} tier building. "
                    f"Estimated materials: {result.cement_bags} cement bags, {result.steel_kg} kg steel, "
                    f"{result.sand_cft} cft sand, {result.aggregate_cft} cft aggregate, {result.bricks_nos:.0f} bricks. "
                    f"Total estimated cost is INR {result.total_cost:,.0f}. "
                    "Explain this simply to a non-technical client in 4-5 sentences, and mention one cost-saving tip."
                )
                explanation = chat_with_llama(prompt, history=[])
                st.write(explanation)
        st.markdown("</div>", unsafe_allow_html=True)
