from datetime import datetime
from io import BytesIO
import os

import pandas as pd
import plotly.express as px
import streamlit as st

from components.cards import metric_card
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from utils.material_engine import MaterialEstimator


# ---------------------------------------------------------
# DYNAMIC TWO-PASS CANVAS FOR PAGE NUMBERS
# ---------------------------------------------------------
class NumberedCanvas(canvas.Canvas):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running header on page 2+
        if self._pageNumber > 1:
            self.drawString(
                54, 750, "ConstructIQ AI — Material Estimation Report"
            )
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 742, 612 - 54, 742)

        # Dynamic Footer on all pages
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 32, page_text)
        self.drawString(
            54, 32, "ConstructIQ AI Enterprise | Material Estimation Report"
        )

        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 44, 612 - 54, 44)

        self.restoreState()


# ---------------------------------------------------------
# MAIN REPORT GENERATION
# ---------------------------------------------------------
def generate_material_report(
    material_df, total_cost, project_type, material_quality, area, floors
):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    primary_color = colors.HexColor("#1E3A8A")
    secondary_color = colors.HexColor("#2563EB")

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=primary_color,
        alignment=TA_LEFT,
        spaceAfter=2,
    )

    subtitle_style = ParagraphStyle(
        "DocSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#4B5563"),
        spaceAfter=8,
    )

    h2_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=primary_color,
        spaceBefore=10,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1F2937"),
    )

    cell_hdr_style = ParagraphStyle(
        "CellHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        textColor=colors.white,
    )

    cell_bold_style = ParagraphStyle(
        "CellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#111827"),
    )

    cell_txt_style = ParagraphStyle(
        "CellTxt",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#374151"),
    )

    story = []

    logo = "assets/logo.png"
    if os.path.exists(logo):
        try:
            story.append(Image(logo, width=2.2 * inch, height=1.4 * inch))
            story.append(Spacer(1, 6))
        except Exception:
            pass

    story.append(Paragraph("ConstructIQ AI Enterprise", title_style))
    story.append(Paragraph("Material Estimation Report", subtitle_style))

    gen_time = datetime.now().strftime("%d %B %Y, %I:%M %p")
    story.append(
        Paragraph(f"<b>Generated:</b> {gen_time}", cell_txt_style)
    )
    story.append(Spacer(1, 8))
    story.append(
        HRFlowable(
            width="100%", thickness=1.5, color=primary_color, spaceAfter=12
        )
    )

    # Project Information Table
    story.append(Paragraph("Project Information", h2_style))

    table_data = [
        [
            Paragraph("Property", cell_hdr_style),
            Paragraph("Value", cell_hdr_style),
        ],
        [
            Paragraph("Project Type", cell_bold_style),
            Paragraph(str(project_type), cell_txt_style),
        ],
        [
            Paragraph("Material Quality", cell_bold_style),
            Paragraph(str(material_quality), cell_txt_style),
        ],
        [
            Paragraph("Area", cell_bold_style),
            Paragraph(f"{area:,.0f} sq.ft", cell_txt_style),
        ],
        [
            Paragraph("Floors", cell_bold_style),
            Paragraph(str(floors), cell_txt_style),
        ],
        [
            Paragraph("Total Materials", cell_bold_style),
            Paragraph(str(len(material_df)), cell_txt_style),
        ],
        [
            Paragraph("Estimated Cost", cell_bold_style),
            Paragraph(f"INR {total_cost:,.0f}", cell_bold_style),
        ],
    ]

    table = Table(table_data, colWidths=[200, 304])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), primary_color),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.HexColor("#F8FAFC"), colors.HexColor("#F1F5F9")],
                ),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 12))

    # Material Requirement Table
    story.append(Paragraph("Material Requirement", h2_style))

    table_data = [
        [
            Paragraph("Material", cell_hdr_style),
            Paragraph("Quantity", cell_hdr_style),
            Paragraph("Cost", cell_hdr_style),
            Paragraph("Availability", cell_hdr_style),
        ]
    ]

    for _, row in material_df.iterrows():
        table_data.append(
            [
                Paragraph(str(row["Material"]), cell_bold_style),
                Paragraph(f"{row['Quantity']:.2f}", cell_txt_style),
                Paragraph(f"INR {row['Cost']:,.0f}", cell_txt_style),
                Paragraph(str(row["Availability"]), cell_txt_style),
            ]
        )

    table = Table(table_data, colWidths=[150, 100, 134, 120])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), secondary_color),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F5F5DC")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 12))

    # AI Procurement Recommendations
    rec_block = []
    rec_block.append(
        Paragraph("AI Procurement Recommendations", h2_style)
    )

    recommendations = [
        "Prioritize procurement of cement and steel.",
        "Purchase bulk materials to reduce transportation cost.",
        "Maintain safety stock for critical materials.",
        "Schedule procurement phase-wise.",
        "Monitor supplier availability regularly.",
    ]

    for item in recommendations:
        rec_block.append(Paragraph(f"• &nbsp; {item}", body_style))
        rec_block.append(Spacer(1, 3))

    rec_block.append(Spacer(1, 8))
    rec_block.append(
        Paragraph(
            "<b>Generated Automatically by ConstructIQ AI Enterprise</b>",
            ParagraphStyle(
                "SubFoot",
                parent=body_style,
                fontName="Helvetica-Bold",
                textColor=primary_color,
            ),
        )
    )
    rec_block.append(
        Paragraph(
            "AI Powered Construction Management Platform", cell_txt_style
        )
    )

    story.append(KeepTogether(rec_block))

    # Build PDF using NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer


# ==========================================================
# MAIN PAGE
# ==========================================================
def show(data):
    st.title("🧱 AI Material Estimation")
    st.caption(
        "Estimate construction materials manually or by uploading a project file."
    )
    st.divider()

    tab1, tab2 = st.tabs(["✏️ Manual Input", "📁 Upload Project File"])

    with tab1:
        manual_estimation(data)

    with tab2:
        upload_estimation(data)

    st.divider()
    st.caption("🧱 ConstructIQ AI Enterprise | Material Estimation")


# ==========================================================
# MANUAL ESTIMATION
# ==========================================================
def manual_estimation(data):
    st.subheader("🏗 Project Details")
    col1, col2 = st.columns(2)

    with col1:
        project_type = st.selectbox(
            "Project Type",
            sorted(data["estimation_rates"]["Project_Type"].unique()),
            key="manual_project",
        )
        area = st.number_input(
            "Built-up Area (sq.ft)",
            min_value=500,
            value=2000,
            step=100,
            key="manual_area",
        )

    with col2:
        material_quality = st.selectbox(
            "Material Quality",
            sorted(
                data["estimation_rates"]["Material_Quality"].unique()
            ),
            key="manual_quality",
        )
        floors = st.number_input(
            "Floors", min_value=1, value=2, key="manual_floor"
        )

    st.divider()

    estimate = st.button(
        "🧱 Calculate Material Requirement",
        use_container_width=True,
        key="manual_button",
    )

    if estimate:
        estimator = MaterialEstimator(data["estimation_materials"])
        material_df, total_cost = estimator.estimate(area)

        display_results(
            material_df=material_df,
            total_cost=total_cost,
            project_type=project_type,
            material_quality=material_quality,
            area=area,
            floors=floors,
        )


# ==========================================================
# UPLOAD PROJECT FILE
# ==========================================================
def upload_estimation(data):
    st.subheader("📁 Upload Project File")
    st.write(
        "Upload a project information file to automatically estimate material requirements."
    )

    sample = pd.DataFrame(
        {
            "Area": [2500],
            "Floors": [3],
            "Project_Type": ["Residential"],
            "Material_Quality": ["Premium"],
        }
    )

    st.download_button(
        "📥 Download Sample CSV",
        sample.to_csv(index=False),
        file_name="sample_material_input.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.divider()

    uploaded_file = st.file_uploader(
        "Upload CSV File",
        type=["csv"],
        help="Upload a project file in the required format.",
    )

    if uploaded_file is None:
        st.info("Please upload a CSV file to continue.")
        return

    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Unable to read file.\n\n{e}")
        return

    st.success("✅ File uploaded successfully.")
    st.subheader("📋 Uploaded Project")
    st.dataframe(df, use_container_width=True, hide_index=True)

    required_columns = [
        "Area",
        "Floors",
        "Project_Type",
        "Material_Quality",
    ]
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        st.error(f"Missing Columns: {', '.join(missing)}")
        return

    st.divider()

    if st.button(
        "🧱 Generate Material Estimate",
        use_container_width=True,
        key="upload_button",
    ):
        try:
            area = float(df.loc[0, "Area"])
            floors = int(df.loc[0, "Floors"])
            project_type = str(df.loc[0, "Project_Type"])
            material_quality = str(df.loc[0, "Material_Quality"])
        except Exception:
            st.error("Invalid values found in uploaded file.")
            return

        estimator = MaterialEstimator(data["estimation_materials"])
        material_df, total_cost = estimator.estimate(area)

        display_results(
            material_df=material_df,
            total_cost=total_cost,
            project_type=project_type,
            material_quality=material_quality,
            area=area,
            floors=floors,
        )


# ==========================================================
# DISPLAY RESULTS FUNCTION
# ==========================================================
def display_results(
    material_df, total_cost, project_type, material_quality, area, floors
):
    total_quantity = material_df["Quantity"].sum()
    highest = material_df.loc[material_df["Cost"].idxmax()]

    st.divider()
    st.success("✅ Material estimation completed successfully.")

    # ---------------------------------------------------
    # EXPORT / DOWNLOAD SECTION PLACED AT TOP
    # ---------------------------------------------------
    st.subheader("📥 Export Material Estimation")

    csv = material_df.to_csv(index=False)
    pdf = generate_material_report(
        material_df, total_cost, project_type, material_quality, area, floors
    )

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📄 Download CSV Data",
            csv,
            file_name="Material_Estimation.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col2:
        st.download_button(
            "📄 Download PDF Report",
            pdf,
            file_name="Material_Estimation_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    st.divider()

    # ---------------------------------------------------
    # MATERIAL SUMMARY
    # ---------------------------------------------------
    st.subheader("📊 Material Summary")

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card(
            "Total Material Cost",
            f"₹ {total_cost/100000:.2f} L",
            "💰",
            "#2563EB",
        )
    with c2:
        metric_card(
            "Total Materials", str(len(material_df)), "🧱", "#22C55E"
        )
    with c3:
        metric_card(
            "Highest Cost Material", highest["Material"], "📈", "#EF4444"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    c4, c5, c6 = st.columns(3)
    with c4:
        metric_card(
            "Built-up Area", f"{area:,.0f} sq.ft", "🏗", "#7C3AED"
        )
    with c5:
        metric_card("Floors", str(floors), "🏢", "#F59E0B")
    with c6:
        metric_card(
            "Total Quantity", f"{total_quantity:,.0f}", "📦", "#0EA5E9"
        )

    st.divider()

    # ---------------------------------------------------
    # PROJECT INFORMATION
    # ---------------------------------------------------
    st.subheader("🏗 Project Information")

    left, right = st.columns(2)
    with left:
        st.container(border=True)
        st.markdown(f"""
**Project Type**
{project_type}

---
**Material Quality**
{material_quality}

---
**Area**
{area:,.0f} sq.ft
""")

    with right:
        st.container(border=True)
        st.markdown(f"""
**Floors**
{floors}

---
**Estimated Materials**
{len(material_df)}

---
**Estimated Cost**
₹ {total_cost:,.0f}
""")

    st.divider()

    # ---------------------------------------------------
    # CHARTS & ANALYTICS
    # ---------------------------------------------------
    st.subheader("📈 Material Analytics")

    chart1, chart2 = st.columns(2)
    with chart1:
        fig = px.pie(
            material_df,
            names="Material",
            values="Cost",
            hole=0.45,
            title="Material Cost Distribution",
        )
        fig.update_layout(
            legend_title="Materials", margin=dict(l=10, r=10, t=50, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)

    with chart2:
        fig = px.bar(
            material_df,
            x="Material",
            y="Quantity",
            color="Material",
            title="Material Quantity",
        )
        fig.update_layout(
            showlegend=False, margin=dict(l=10, r=10, t=50, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---------------------------------------------------
    # MATERIAL REQUIREMENT TABLE
    # ---------------------------------------------------
    st.subheader("📋 Material Requirement")

    display_df = material_df.copy()
    display_df["Quantity"] = display_df["Quantity"].round(2)
    display_df["Cost"] = display_df["Cost"].round(2)

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.divider()

    # ---------------------------------------------------
    # PROCUREMENT SUMMARY
    # ---------------------------------------------------
    st.subheader("📦 Procurement Summary")

    high = material_df[material_df["Availability"] == "High"]
    medium = material_df[material_df["Availability"] == "Medium"]
    low = material_df[material_df["Availability"] == "Low"]

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("High Availability", len(high), "✅", "#16A34A")
    with c2:
        metric_card("Medium Availability", len(medium), "⚠️", "#D97706")
    with c3:
        metric_card("Low Availability", len(low), "❌", "#DC2626")

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------
    # AVAILABILITY STATUS
    # ---------------------------------------------------
    st.subheader("🚚 Material Availability")

    for _, row in material_df.iterrows():
        material = row["Material"]
        availability = row["Availability"]

        if availability == "High":
            st.success(f"✅ {material} — High Availability")
        elif availability == "Medium":
            st.warning(f"⚠️ {material} — Medium Availability")
        else:
            st.error(f"❌ {material} — Low Availability")

    st.divider()

    # ---------------------------------------------------
    # PROCUREMENT INSIGHTS & AI RECOMMENDATION
    # ---------------------------------------------------
    st.subheader("📈 Procurement Insights")

    highest_cost = material_df.loc[material_df["Cost"].idxmax()]
    highest_quantity = material_df.loc[material_df["Quantity"].idxmax()]

    c1, c2 = st.columns(2)
    with c1:
        st.info(f"""
### 💰 Highest Cost Material
**Material:** {highest_cost['Material']}  
**Estimated Cost:** ₹ {highest_cost['Cost']:,.0f}  

This material contributes the highest share of the procurement budget.
""")
    with c2:
        st.info(f"""
### 📦 Highest Quantity Material
**Material:** {highest_quantity['Material']}  
**Quantity:** {highest_quantity['Quantity']:,.2f}  

Bulk procurement can reduce transportation and purchase costs.
""")

    st.divider()

    st.subheader("🤖 AI Procurement Recommendation")
    st.info(f"""
* Estimated material cost is **₹ {total_cost:,.0f}**.
* Procure **cement, steel and aggregates** first since they account for the largest portion of project expenditure.
* Purchase high-volume materials in bulk to reduce transportation and procurement costs.
* Schedule procurement according to construction phases to avoid material wastage.
* Continuously monitor supplier availability to minimize project delays.
""")
