import json
import streamlit as st
from PIL import Image
from database.db import get_db
from database import models
from utils.cv_analyzer import analyze_site_image, bgr_to_rgb
from utils.styling import page_hero, stat_card, status_strip


def _get_project_id() -> int | None:
    with get_db() as conn:
        project = models.get_default_project(conn)
        return int(project["id"]) if project else None


def _severity_color(severity: str) -> str:
    return {"pass": "#00E676", "warning": "#FFAB00", "danger": "#FF5252"}.get(severity, "#8B949E")


def render():
    page_hero(
        "👁️", "Computer Vision Site Inspection",
        "OpenCV-powered PPE compliance &amp; hazard detection with DB logging",
        badge="AI VISION ENGINE"
    )

    st.markdown("""
        <div class="hub-card" style="margin-bottom: 18px; padding: 16px 20px;">
            <h4>📸 Image Upload & Analysis</h4>
            <span class="hub-card-tag">Upload a site photo to run automated inspection</span>
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Site Image (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)

        col1, col2 = st.columns([1, 1], gap="large")

        with st.spinner("🔍 Running computer vision analysis..."):
            try:
                result = analyze_site_image(image)
                analysis_ok = True
            except ImportError as exc:
                st.error(f"⚠️ Computer vision dependencies not installed: {exc}")
                analysis_ok = False
                result = None
            except Exception as exc:
                st.error(f"⚠️ Image analysis failed: {exc}")
                analysis_ok = False
                result = None

        if analysis_ok and result:
            with col1:
                st.markdown("<p style='color: #8B949E; font-weight: 600; font-size: 0.9rem;'>ANNOTATED SITE FRAME</p>", unsafe_allow_html=True)
                if result.annotated_image is not None:
                    st.image(bgr_to_rgb(result.annotated_image), caption="CV Analysis Overlay", use_container_width=True)
                else:
                    st.image(image, caption="Uploaded Construction Site Image", use_container_width=True)

            with col2:
                st.markdown("<p style='color: #8B949E; font-weight: 600; font-size: 0.9rem;'>AUTOMATED ANALYSIS REPORT</p>", unsafe_allow_html=True)

                st.markdown(status_strip(
                    result.status_color,
                    f"{'✅' if result.overall_score >= 85 else '⚠️'} {result.status}",
                    f"Overall PPE compliance score: {result.overall_score}% — {result.estimated_personnel} personnel detected by AI.",
                ), unsafe_allow_html=True)

                m1, m2 = st.columns(2)
                with m1:
                    h_color = "#00E676" if result.hardhat_compliance_pct >= 85 else "#FFAB00"
                    st.markdown(stat_card("🪖", "Hardhat Compliance", f"{result.hardhat_compliance_pct}%", None, h_color), unsafe_allow_html=True)
                with m2:
                    v_color = "#00E676" if result.vest_compliance_pct >= 90 else "#FFAB00"
                    st.markdown(stat_card("🦺", "Safety Vest Compliance", f"{result.vest_compliance_pct}%", None, v_color), unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<h5 style='color: #F0F6FC; margin-bottom: 10px;'>Detailed Audit Breakdown</h5>", unsafe_allow_html=True)

                for finding in result.findings:
                    color = _severity_color(finding.severity)
                    icon = "✅" if finding.severity == "pass" else "⚠️"
                    st.markdown(status_strip(color, f"{icon} {finding.title}", finding.message), unsafe_allow_html=True)

                project_id = _get_project_id()
                if project_id and st.button("💾 Save Inspection to Database", type="primary", use_container_width=True):
                    with get_db() as conn:
                        insp_id = models.create_inspection(
                            conn,
                            result=result.status,
                            checklist_json=json.dumps(result.to_dict()),
                            project_id=project_id,
                            inspector=st.session_state.get("username", "CV Engine"),
                        )
                    st.success(f"✅ Inspection #{insp_id} saved to project records.")

    else:
        st.markdown("""
            <div class="hub-card" style="text-align:center; padding: 40px 20px;">
                <div style="font-size: 2.2rem; margin-bottom: 8px;">🖼️</div>
                <h4>No Image Uploaded Yet</h4>
                <p class="hub-card-body">Upload a site photo above to see PPE compliance scoring and hazard detection results here.</p>
            </div>
        """, unsafe_allow_html=True)

    # Recent inspections
    project_id = _get_project_id()
    if project_id:
        with get_db() as conn:
            inspections = models.list_inspections(conn, project_id, limit=5)
        if inspections:
            st.markdown("<hr class='hub-divider'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #00E5FF;'>📋 Recent CV Inspections</h4>", unsafe_allow_html=True)
            for insp in inspections:
                st.markdown(f"""
                    <div class="hub-strip" style="border-left-color: #00E5FF;">
                        <b>{insp['result']}</b> — {insp['inspection_date']}
                        <p>Inspector: {insp['inspector']}</p>
                    </div>
                """, unsafe_allow_html=True)
