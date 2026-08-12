from datetime import datetime
from io import BytesIO
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
    HRFlowable
)

import streamlit as st


# =====================================================
# CORPORATE COLOR PALETTE
# =====================================================

PRIMARY = colors.HexColor("#0F172A")
BLUE = colors.HexColor("#2563EB")
LIGHT_BLUE = colors.HexColor("#EFF6FF")
GRAY = colors.HexColor("#64748B")
LIGHT = colors.HexColor("#F8FAFC")
BORDER = colors.HexColor("#D1D5DB")


# =====================================================
# PAGE HEADER / FOOTER
# =====================================================

class NumberedCanvas(canvas.Canvas):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_header_footer(total)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_header_footer(self, total):
        self.saveState()

        # Top decorative bar
        self.setFillColor(PRIMARY)
        self.rect(0, 832, 595, 10, fill=True, stroke=False)

        # Header (Pages 2+)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(GRAY)
            self.drawString(45, 807, "CONSTRUCTIQ AI ENTERPRISE")
            self.drawRightString(550, 807, datetime.now().strftime("%d %b %Y"))
            self.setStrokeColor(BORDER)
            self.setLineWidth(0.5)
            self.line(45, 800, 550, 800)

        # Footer (All pages)
        self.setFont("Helvetica", 8)
        self.setFillColor(GRAY)
        self.setStrokeColor(BORDER)
        self.setLineWidth(0.5)
        self.line(45, 45, 550, 45)

        self.drawString(45, 30, "ConstructIQ AI Enterprise — Confidential")
        self.drawRightString(550, 30, f"Page {self._pageNumber} of {total}")

        self.restoreState()


# =====================================================
# PDF GENERATOR FUNCTION
# =====================================================

def generate_report(data):

    projects = data["projects"]
    delays = data["delays"]
    rework = data["rework"]
    safety = data["safety"]

    # Metrics Calculation
    total_projects = len(projects)
    completed = len(projects[projects["Current_Status"] == "Completed"])
    delayed = len(projects[projects["Current_Status"] == "Delayed"])

    budget = projects["Budget_INR"].sum()
    spent = projects["Actual_Cost_INR"].sum()
    remaining = budget - spent
    utilization = (spent / budget * 100) if budget else 0.0

    completion = projects["Completion_Percentage"].mean()
    safety_score = safety["Overall_Safety_Score"].mean()
    total_rework = rework["Rework_Cost"].sum()
    avg_delay = delays["Delay_Days"].mean()

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=50,
        bottomMargin=55,
        leftMargin=45,
        rightMargin=45
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=30,
        alignment=TA_CENTER,
        textColor=PRIMARY
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=PRIMARY,
        spaceAfter=6,
        spaceBefore=12
    )

    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=15,
        textColor=PRIMARY
    )

    kpi_val_style = ParagraphStyle(
        "KPIValue",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=PRIMARY
    )

    kpi_lbl_style = ParagraphStyle(
        "KPILabel",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=GRAY
    )

    story = []

    # =====================================================
    # COVER PAGE
    # =====================================================

    logo_path = "assets/logo.png"
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=2.8 * inch, height=2.0 * inch))
        story.append(Spacer(1, 15))
    else:
        story.append(Spacer(1, 40))

    story.append(Paragraph("CONSTRUCTIQ AI ENTERPRISE", title_style))
    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "<b>AI Powered Construction Intelligence Platform</b>",
            ParagraphStyle("SubTitle", fontName="Helvetica-Bold", fontSize=14, leading=18, alignment=TA_CENTER, textColor=BLUE)
        )
    )

    story.append(Spacer(1, 60))

    story.append(
        Paragraph(
            "Executive Portfolio Report",
            ParagraphStyle("ReportType", fontName="Helvetica-Bold", fontSize=20, leading=24, alignment=TA_CENTER, textColor=PRIMARY)
        )
    )

    story.append(Spacer(1, 50))

    meta_text = f"""
    Generated on<br/>
    <b>{datetime.now().strftime("%d %B %Y")}</b><br/><br/>
    Version 1.0<br/><br/>
    <i>Infosys Springboard Internship</i>
    """
    story.append(
        Paragraph(
            meta_text,
            ParagraphStyle("MetaText", fontName="Helvetica", alignment=TA_CENTER, fontSize=11, leading=18, textColor=GRAY)
        )
    )

    story.append(PageBreak())

    # =====================================================
    # EXECUTIVE SUMMARY
    # =====================================================

    story.append(Paragraph("Executive Summary", heading_style))
    story.append(HRFlowable(width="100%", color=BLUE, thickness=2, spaceAfter=12))

    summary_text = """
    ConstructIQ AI Enterprise is an AI-powered construction management platform designed to assist project managers, 
    engineers, and stakeholders in monitoring and analyzing construction projects.<br/><br/>
    The platform integrates project management, budget analysis, cost estimation, material estimation, delay prediction, 
    construction rework, site safety, risk intelligence, document management, daily reporting, and predictive AI analytics.<br/><br/>
    This executive report summarizes the current status of the entire project portfolio using real-time project data 
    and AI-generated insights to support informed decision-making.
    """
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 30))

    # =====================================================
    # EXECUTIVE KPI DASHBOARD
    # =====================================================

    story.append(Paragraph("Executive KPI Dashboard", heading_style))
    story.append(Paragraph("Key performance metrics providing a portfolio-wide status summary:", body_style))
    story.append(Spacer(1, 10))

    def make_kpi_card(title, value):
        return Table(
            [[Paragraph(f"<b>{value}</b>", kpi_val_style)],
             [Paragraph(title, kpi_lbl_style)]],
            colWidths=[120],
            rowHeights=[22, 18]
        )

    row1 = [
        make_kpi_card("Total Projects", str(total_projects)),
        make_kpi_card("Completed", str(completed)),
        make_kpi_card("Delayed", str(delayed)),
        make_kpi_card("Total Budget", f"INR {budget/1e7:.2f} Cr")
    ]

    t1 = Table([row1], colWidths=[126, 126, 126, 126])
    t1.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t1)
    story.append(Spacer(1, 10))

    row2 = [
        make_kpi_card("Completion Rate", f"{completion:.1f}%"),
        make_kpi_card("Safety Score", f"{safety_score:.1f}/100"),
        make_kpi_card("Rework Cost", f"INR {total_rework/1e7:.2f} Cr"),
        make_kpi_card("Budget Used", f"{utilization:.1f}%")
    ]

    t2 = Table([row2], colWidths=[126, 126, 126, 126])
    t2.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t2)
    story.append(Spacer(1, 30))

    # =====================================================
    # FINANCIAL ANALYSIS
    # =====================================================

    story.append(Paragraph("Financial Analysis", heading_style))

    fin_data = [
        ["Metric", "Value"],
        ["Total Portfolio Budget", f"INR {budget:,.0f}"],
        ["Actual Expenditure", f"INR {spent:,.0f}"],
        ["Remaining Allocation", f"INR {remaining:,.0f}"],
        ["Budget Utilization", f"{utilization:.1f}%"],
        ["Average Progress Completion", f"{completion:.1f}%"]
    ]

    financial_table = Table(fin_data, colWidths=[250, 255])
    financial_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (1, 0), (1, -1), "CENTER")
    ]))
    story.append(financial_table)
    story.append(Spacer(1, 12))

    financial_note = f"""
    <b>AI Financial Observation:</b> Overall budget utilization across active projects is currently at <b>{utilization:.1f}%</b>. 
    The remaining allocation is <b>INR {remaining:,.0f}</b>. Capital expenditure remains within acceptable bounds, though 
    rigorous variance tracking is advised for high-value structural components.
    """
    
    fin_box = Table([[Paragraph(financial_note, body_style)]], colWidths=[505])
    fin_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
        ("BOX", (0, 0), (-1, -1), 1, BLUE),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10)
    ]))
    story.append(fin_box)
    story.append(Spacer(1, 20))

    story.append(PageBreak())
    # =====================================================
    # DELAY INTELLIGENCE
    # =====================================================

    story.append(Paragraph("Delay Intelligence & Schedule Risks", heading_style))

    if not delays.empty:
        top_delay = delays.loc[delays["Delay_Days"].idxmax()]
        max_delay_days = top_delay["Delay_Days"]
        affected_project = str(top_delay["Project_ID"])
        delay_reason = str(top_delay["Reason"])
    else:
        max_delay_days = 0
        affected_project = "N/A"
        delay_reason = "N/A"

    delay_data = [
        ["Indicator", "Value"],
        ["Average Delay across Portfolio", f"{avg_delay:.1f} Days"],
        ["Maximum Recorded Delay", f"{max_delay_days} Days"],
        ["Most Affected Project ID", affected_project],
        ["Primary Critical Reason", delay_reason]
    ]

    delay_table = Table(delay_data, colWidths=[250, 255])
    delay_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(delay_table)
    story.append(Spacer(1, 20))


    # =====================================================
    # PORTFOLIO PERFORMANCE TABLE
    # =====================================================

    story.append(Paragraph("Portfolio Performance Overview", heading_style))

    table_data = [["Project Name", "Status", "Completion", "Budget (Cr)"]]

    for _, row in projects.head(10).iterrows():
        table_data.append([
            str(row["Project_Name"]),
            str(row["Current_Status"]),
            f"{row['Completion_Percentage']}%",
            f"{row['Budget_INR']/1e7:.2f}"
        ])

    portfolio_table = Table(table_data, colWidths=[215, 90, 100, 100])
    portfolio_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (1, 0), (-1, -1), "CENTER")
    ]))
    story.append(portfolio_table)
    story.append(Spacer(1, 20))

    # =====================================================
    # SITE SAFETY & REWORK ANALYSIS
    # =====================================================

    story.append(Paragraph("Site Safety & Quality Compliance", heading_style))

    safe = len(safety[safety["Overall_Safety_Score"] >= 85])
    warning = len(safety[(safety["Overall_Safety_Score"] >= 70) & (safety["Overall_Safety_Score"] < 85)])
    critical = len(safety[safety["Overall_Safety_Score"] < 70])

    safety_data = [
        ["Safety Metric", "Value"],
        ["Average Portfolio Safety Score", f"{safety_score:.1f} / 100"],
        ["High Compliance Sites (≥85)", str(safe)],
        ["Moderate Caution Sites (70-84)", str(warning)],
        ["Critical Risk Sites (<70)", str(critical)]
    ]

    safety_table = Table(safety_data, colWidths=[250, 255])
    safety_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6)
    ]))
    story.append(safety_table)
    story.append(Spacer(1, 20))

    story.append(PageBreak())
    # =====================================================
    # AI EXECUTIVE RECOMMENDATIONS
    # =====================================================

    story.append(Paragraph("AI Executive Recommendations", heading_style))

    recommendations = [
        "Optimize procurement planning to reduce lead-time schedule delays.",
        "Monitor budget utilization on a weekly cadence to prevent localized cost overruns.",
        "Increase quality assurance (QA/QC) inspections during critical structural phases.",
        "Improve tier-1 supplier performance tracking and delivery alignment.",
        "Enforce mandatory weekly safety audits and toolbox talks on high-risk job sites."
    ]

    rec_rows = []
    for i, item in enumerate(recommendations, 1):
        rec_rows.append([
            Paragraph(f"<b>{i}.</b>", body_style),
            Paragraph(item, body_style)
        ])

    rec_table = Table(rec_rows, colWidths=[25, 480])
    rec_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
        ("GRID", (0, 0), (-1, -1), 0.3, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6)
    ]))
    story.append(rec_table)

    # Build PDF Document
    doc.build(story, canvasmaker=NumberedCanvas)
    
    buffer.seek(0)
    return buffer


# =====================================================
# STREAMLIT PAGE MODULE FUNCTION (Fixes AttributeError)
# =====================================================

def show(data):
    st.header("📄 Executive Portfolio Report")
    st.write("Generate and download enterprise PDF analytics reports dynamically compiled from portfolio metrics.")

    st.divider()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Report Contents Summary")
        st.markdown("""
        - **Executive Summary**: High-level status and AI observations.
        - **KPI Dashboard**: Total projects, budget metrics, completion rate, and safety score.
        - **Financial Analysis**: Spend tracking and utilization breakdowns.
        - **Delay Intelligence**: Critical schedule risks and root causes.
        - **Safety & Rework Performance**: Quality compliance metrics.
        - **AI Recommendations**: Tactical suggestions generated by AI models.
        """)

    with col2:
        st.subheader("Generate PDF")
        if st.button("Generate Executive Report", type="primary", use_container_width=True):
            with st.spinner("Building PDF report..."):
                pdf_bytes = generate_report(data)
                
                st.success("Report ready!")
                st.download_button(
                    label="📥 Download PDF Document",
                    data=pdf_bytes,
                    file_name=f"ConstructIQ_Executive_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )