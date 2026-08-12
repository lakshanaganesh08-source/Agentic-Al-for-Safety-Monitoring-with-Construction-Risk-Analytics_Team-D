import streamlit as st

from utils.estimation_engine import CostEstimator
from components.cards import metric_card
from components.charts import cost_breakdown_chart
from components.charts import cost_bar_chart

from io import BytesIO
from datetime import datetime


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


class NumberedCanvas(canvas.Canvas):
    """Canvas that computes total pages in a first pass and renders header/footer page numbers on the second pass."""

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
        self.setFillColor(colors.HexColor("#6B7280"))

        # Running header on page 2+
        if self._pageNumber > 1:
            self.drawString(54, 750, "ConstructIQ AI — Cost Estimation Report")
            self.setStrokeColor(colors.HexColor("#E5E7EB"))
            self.setLineWidth(0.5)
            self.line(54, 742, 612 - 54, 742)

        # Dynamic Footer on all pages
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 32, page_text)
        self.drawString(
            54, 32, "Confidential — ConstructIQ AI Enterprise Platform"
        )

        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 44, 612 - 54, 44)

        self.restoreState()


def generate_cost_report(
    project_name,
    client,
    location,
    project_type,
    priority,
    material_quality,
    area,
    floors,
    foundation,
    weather,
    material_availability,
    contingency,
    inflation,
    result,
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

    # Original Colors Preserved
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

    try:
        story.append(
            Image("assets/logo.png", width=2.2 * inch, height=1.4 * inch)
        )
        story.append(Spacer(1, 6))
    except Exception:
        pass

    # Header Block
    story.append(Paragraph("ConstructIQ AI Enterprise", title_style))
    story.append(
        Paragraph("AI Construction Cost Estimation Report", subtitle_style)
    )

    gen_time = datetime.now().strftime("%d %B %Y | %I:%M %p")
    story.append(
        Paragraph(f"<b>Generated on:</b> {gen_time}", cell_txt_style)
    )
    story.append(Spacer(1, 8))
    story.append(
        HRFlowable(
            width="100%", thickness=1.5, color=primary_color, spaceAfter=12
        )
    )

    # ---------------------------------------------------
    # Project Details Table
    # ---------------------------------------------------
    story.append(Paragraph("Project Details & Parameters", h2_style))

    table_data = [
        [
            Paragraph("Field", cell_hdr_style),
            Paragraph("Value", cell_hdr_style),
        ],
        [
            Paragraph("Project Name", cell_bold_style),
            Paragraph(str(project_name or "-"), cell_txt_style),
        ],
        [
            Paragraph("Client", cell_bold_style),
            Paragraph(str(client or "-"), cell_txt_style),
        ],
        [
            Paragraph("Location", cell_bold_style),
            Paragraph(str(location or "-"), cell_txt_style),
        ],
        [
            Paragraph("Project Type", cell_bold_style),
            Paragraph(str(project_type or "-"), cell_txt_style),
        ],
        [
            Paragraph("Priority", cell_bold_style),
            Paragraph(str(priority or "-"), cell_txt_style),
        ],
        [
            Paragraph("Material Quality", cell_bold_style),
            Paragraph(str(material_quality or "-"), cell_txt_style),
        ],
        [
            Paragraph("Built-up Area", cell_bold_style),
            Paragraph(f"{area:,} sq.ft", cell_txt_style),
        ],
        [
            Paragraph("Floors", cell_bold_style),
            Paragraph(str(floors), cell_txt_style),
        ],
        [
            Paragraph("Foundation", cell_bold_style),
            Paragraph(str(foundation), cell_txt_style),
        ],
        [
            Paragraph("Weather Risk", cell_bold_style),
            Paragraph(str(weather), cell_txt_style),
        ],
        [
            Paragraph("Material Availability", cell_bold_style),
            Paragraph(str(material_availability), cell_txt_style),
        ],
        [
            Paragraph("Inflation", cell_bold_style),
            Paragraph(f"{inflation}%", cell_txt_style),
        ],
        [
            Paragraph("Contingency", cell_bold_style),
            Paragraph(f"{contingency}%", cell_txt_style),
        ],
    ]

    t1 = Table(table_data, colWidths=[190, 314])
    t1.setStyle(
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
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(t1)

    story.append(Spacer(1, 12))

    # ---------------------------------------------------
    # Estimated Cost Table
    # ---------------------------------------------------
    story.append(Paragraph("Estimated Cost Summary", h2_style))

    total_cr = result["Total Cost"] / 10000000
    mat_cr = result["Material"] / 10000000
    lab_cr = result["Labour"] / 10000000
    eq_cr = result["Equipment"] / 10000000
    misc_cr = result["Misc"] / 10000000

    cost_table_data = [
        [
            Paragraph("Category", cell_hdr_style),
            Paragraph("Amount / Estimate", cell_hdr_style),
        ],
        [
            Paragraph("Total Cost", cell_bold_style),
            Paragraph(f"INR {total_cr:.2f} Cr", cell_bold_style),
        ],
        [
            Paragraph("Material Cost", cell_bold_style),
            Paragraph(f"INR {mat_cr:.2f} Cr", cell_txt_style),
        ],
        [
            Paragraph("Labour Cost", cell_bold_style),
            Paragraph(f"INR {lab_cr:.2f} Cr", cell_txt_style),
        ],
        [
            Paragraph("Equipment Cost", cell_bold_style),
            Paragraph(f"INR {eq_cr:.2f} Cr", cell_txt_style),
        ],
        [
            Paragraph("Miscellaneous", cell_bold_style),
            Paragraph(f"INR {misc_cr:.2f} Cr", cell_txt_style),
        ],
        [
            Paragraph("Estimated Duration", cell_bold_style),
            Paragraph(f"{result['Duration']} Months", cell_bold_style),
        ],
    ]

    t2 = Table(cost_table_data, colWidths=[210, 294])
    t2.setStyle(
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
    story.append(t2)

    story.append(Spacer(1, 12))

    # ---------------------------------------------------
    # AI Recommendations (Kept together to prevent splits)
    # ---------------------------------------------------
    rec_block = []
    rec_block.append(Paragraph("AI Recommendations", h2_style))

    recommendations = [
        "Bulk procurement can reduce material cost.",
        "Monitor inflation for long-term projects.",
        "Premium materials improve durability.",
        "Allocate labour efficiently to avoid delays.",
        "Maintain contingency between 5% and 10%.",
        "Schedule critical work during favourable weather.",
    ]

    for r in recommendations:
        rec_block.append(Paragraph(f"• &nbsp; {r}", body_style))
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
            "AI-Powered Construction Management Platform", cell_txt_style
        )
    )

    story.append(KeepTogether(rec_block))

    # Build with two-pass canvas for dynamic footer page numbers
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer

def show(data):
    st.title("💰 AI Construction Cost Estimation")
    st.caption(
        "Predict construction cost, duration and resource allocation using AI-powered estimation."
    )
    st.divider()

    # ==================================================
    # PROJECT INFORMATION
    # ==================================================
    st.subheader("🏗️ Project Information")
    col1, col2 = st.columns(2)

    with col1:
        project_name = st.text_input("Project Name", placeholder="Enter project name")
        client = st.text_input("Client Name", placeholder="Enter client name")
        project_type = st.selectbox(
            "Project Type",
            sorted(data["estimation_rates"]["Project_Type"].unique())
        )

    with col2:
        location = st.text_input("Location", placeholder="Enter project location")
        priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        material_quality = st.selectbox(
            "Material Quality",
            sorted(data["estimation_rates"]["Material_Quality"].unique())
        )

    st.divider()

    # ==================================================
    # CONSTRUCTION DETAILS
    # ==================================================
    st.subheader("📐 Construction Details")
    col1, col2, col3 = st.columns(3)

    with col1:
        area = st.number_input("Built-up Area (sq.ft)", min_value=500, value=2000, step=100)
    with col2:
        floors = st.number_input("Number of Floors", min_value=1, value=2)
    with col3:
        foundation = st.selectbox(
            "Foundation Type",
            ["Shallow Foundation", "Pile Foundation", "Raft Foundation"]
        )

    st.divider()

    # ==================================================
    # EXTERNAL FACTORS
    # ==================================================
    st.subheader("🌦️ External Factors")
    col1, col2 = st.columns(2)

    with col1:
        weather = st.selectbox("Weather Risk", ["Low", "Medium", "High"])
        inflation = st.slider("Inflation (%)", 0, 20, 5)

    with col2:
        material_availability = st.selectbox("Material Availability", ["High", "Medium", "Low"])
        contingency = st.slider("Contingency (%)", 0, 20, 5)

    st.divider()

    estimate = st.button("💰 Estimate Project Cost", use_container_width=True)

    # ==================================================
    # ESTIMATION
    # ==================================================
    if estimate:
        estimator = CostEstimator(data["estimation_rates"])

        try:
            result = estimator.estimate(
                project_type=project_type,
                material_quality=material_quality,
                area=area,
                floors=floors,
                contingency=contingency,
                inflation=inflation
            )
        except Exception as e:
            st.error(str(e))
            st.stop()

        # Generate and render PDF download link here now that variables are populated
        pdf = generate_cost_report(
            project_name, client, location, project_type, priority,
            material_quality, area, floors, foundation, weather,
            material_availability, contingency, inflation, result
        )

        st.download_button(
            "📥 Download Cost Estimation Report",
            pdf,
            file_name="ConstructIQ_Cost_Estimation_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        st.success("✅ Project estimation completed successfully.")
        st.divider()

        st.subheader("📊 Estimated Cost Summary")
        col1, col2, col3 = st.columns(3)

        with col1:
            metric_card(
                "Estimated Cost",
                f"₹ {result['Total Cost']/10000000:.2f} Cr",
                "💰", "#2563EB", "Predicted Total Cost"
            )
        with col2:
            metric_card(
                "Material Cost",
                f"₹ {result['Material']/10000000:.2f} Cr",
                "🧱", "#22C55E", "Construction Materials"
            )
        with col3:
            metric_card(
                "Labour Cost",
                f"₹ {result['Labour']/10000000:.2f} Cr",
                "👷", "#F97316", "Labour Charges"
            )

        st.markdown("<br>", unsafe_allow_html=True)
        col4, col5 = st.columns(2)

        with col4:
            metric_card(
                "Equipment Cost",
                f"₹ {result['Equipment']/10000000:.2f} Cr",
                "🚜", "#7C3AED", "Equipment Usage"
            )
        with col5:
            metric_card(
                "Estimated Duration",
                f"{result['Duration']} Months",
                "📅", "#EF4444", "Expected Completion"
            )

        st.divider()
        st.divider()

        st.subheader("📊 Cost Analytics")
        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(cost_breakdown_chart(result), use_container_width=True)
        with col2:
            st.plotly_chart(cost_bar_chart(result), use_container_width=True)

        st.subheader("📋 Project Summary")
        c1, c2 = st.columns(2)

        with c1:
            st.container(border=True)
            st.markdown(f"""
**Project Name**
{project_name}

---
**Client**
{client}

---
**Location**
{location}

---
**Project Type**
{project_type}

---
**Priority**
{priority}
""")

        with c2:
            st.container(border=True)
            st.markdown(f"""
**Built-up Area**
{area:,} sq.ft

---
**Floors**
{floors}

---
**Foundation**
{foundation}

---
**Material Quality**
{material_quality}

---
**Weather Risk**
{weather}
""")

        st.divider()

        st.subheader("⚠ Risk Assessment")
        if weather == "High":
            st.error("High weather risk may increase project duration.")
        elif weather == "Medium":
            st.warning("Moderate weather impact expected.")
        else:
            st.success("Weather conditions are favorable.")

        if material_availability == "Low":
            st.error("Material availability is low. Procurement delays are possible.")
        elif material_availability == "Medium":
            st.warning("Monitor material procurement carefully.")
        else:
            st.success("Material availability is good.")

        if inflation > 10:
            st.warning("High inflation may increase the project budget.")
        if contingency < 5:
            st.warning("Consider increasing contingency for unexpected expenses.")

        st.divider()

        st.subheader("🤖 AI Recommendation")
        st.info(
            """
        * Premium materials increase durability but also raise project costs.
        * Bulk purchasing of steel and cement can reduce procurement expenses.
        * Monitor weather forecasts before scheduling critical construction activities.
        * Review labour allocation regularly to avoid delays.
        * Ollama AI-powered optimization and intelligent recommendations will be integrated in the next phase.
        """
        )

    st.divider()
    st.caption("💰 ConstructIQ AI Enterprise | Cost Estimation")