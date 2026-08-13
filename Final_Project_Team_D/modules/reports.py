import streamlit as st
import pandas as pd
from datetime import datetime
from database.db import get_db
from database import models
from utils.report_builder import create_report_bytes, make_archive
from utils.styling import page_hero


def _get_project_id() -> int | None:
    with get_db() as conn:
        project = models.get_default_project(conn)
        return int(project["id"]) if project else None


def render():
    page_hero(
        "📄", "Export Project Reports",
        "Generate live reports from SQLite data — PDF, Excel, CSV, JSON &amp; more",
        badge="REPORTING SUITE"
    )

    st.markdown("""
        <div class="hub-card" style="padding: 16px 20px; margin-bottom: 18px;">
            <h4>⚙️ Report Export Configuration</h4>
            <span class="hub-card-tag">Reports pull live data from your project database</span>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        report_type = st.selectbox(
            "📋 Select Report Type",
            [
                "Monthly Cost Analysis",
                "Safety & Compliance Audit",
                "Full Site Progress Summary",
                "Executive Report",
                "Project Health Report",
                "Audit Report",
            ],
            help="Choose the analytical domain to include in the generated report."
        )

        descriptions = {
            "Monthly Cost Analysis": ("#00E5FF", "💰 Budget variances, material costs, labor allocations from DB."),
            "Safety & Compliance Audit": ("#00E676", "🦺 Incident logs, hazard counts, and OSHA audit checks."),
            "Full Site Progress Summary": ("#FFAB00", "📊 Task milestones, progress %, and delay risk metrics."),
            "Executive Report": ("#7C3AED", "📈 Comprehensive executive KPI dashboard with all agent scores."),
            "Project Health Report": ("#00E676", "🏥 Overall project wellness assessment and recommendations."),
            "Audit Report": ("#FF5252", "🔍 Comprehensive audit of compliance, safety, and operational standards."),
        }
        color, desc = descriptions[report_type]
        st.markdown(f"""
            <div class="hub-strip" style="border-left-color:{color};">
                <p style="margin:0;">{desc}</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        file_format = st.radio(
            "📂 Export Format",
            ["PDF", "CSV", "Excel", "TXT", "JSON", "Word", "All Files"],
            horizontal=True,
            help="PDF uses ReportLab; Excel uses openpyxl."
        )

        display_format = file_format if file_format != "All Files" else "ZIP Bundle"
        st.markdown(f"""
            <div class="hub-card" style="text-align: center; padding: 16px;">
                <span style="color: #8B949E; font-size: 0.8rem; font-weight: 600;">SELECTED OUTPUT</span>
                <p style="color: #F0F6FC; font-size: 1.1rem; font-weight: 700; margin: 4px 0 0 0;">
                    {report_type} <span style="color: #00E5FF;">({display_format})</span>
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Generate Report Package", type="primary", key="generate_report", use_container_width=True):
        try:
            if file_format == "All Files":
                bytes_data = make_archive(report_type)
                mime_type = "application/zip"
                file_name = report_type.lower().replace(" ", "_") + ".zip"
            else:
                bytes_data, mime_type, extension = create_report_bytes(report_type, file_format)
                file_name = report_type.lower().replace(" ", "_") + f".{extension}"

            project_id = _get_project_id()
            if project_id:
                with get_db() as conn:
                    models.create_report(
                        conn,
                        report_type=report_type,
                        period=datetime.now().strftime("%Y-%m"),
                        file_path=file_name,
                        project_id=project_id,
                    )

            st.markdown("<hr class='hub-divider'>", unsafe_allow_html=True)
            st.markdown("""
                <div class="hub-card" style="text-align: center; border-color: rgba(0,229,255,0.4); margin-bottom: 20px;">
                    <span style="color: #00E5FF; font-weight: 700;">✅ Report Successfully Generated!</span>
                    <p class="hub-card-body">Live database metrics included. Ready for download.</p>
                </div>
            """, unsafe_allow_html=True)

            st.download_button(
                label=f"📥 Download {report_type} ({display_format})",
                data=bytes_data,
                file_name=file_name,
                mime=mime_type,
                use_container_width=True,
            )
        except Exception as exc:
            st.error(f"⚠️ Report generation failed: {exc}")

    # Report history
    project_id = _get_project_id()
    if project_id:
        with get_db() as conn:
            reports = models.list_reports(conn, project_id, limit=10)
        if reports:
            st.markdown("<hr class='hub-divider'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #00E5FF;'>📋 Generated Report History</h4>", unsafe_allow_html=True)
            history = [
                {
                    "Type": r["report_type"],
                    "Period": r.get("period") or "—",
                    "File": r.get("file_path") or "—",
                    "Generated": r["generated_at"],
                }
                for r in reports
            ]
            st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)
