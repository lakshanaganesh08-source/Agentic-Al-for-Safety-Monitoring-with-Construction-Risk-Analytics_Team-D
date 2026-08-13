import re
import io
from datetime import datetime

import streamlit as st
from utils.llama_client import chat_with_llama


def _extract_text(uploaded_file) -> str:
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    text += (page.extract_text() or "") + "\n"
            return text
        except Exception as e:
            return f"[Could not parse PDF: {e}]"
    elif name.endswith(".docx"):
        try:
            import docx
            d = docx.Document(uploaded_file)
            return "\n".join(p.text for p in d.paragraphs)
        except Exception as e:
            return f"[Could not parse DOCX: {e}]"
    else:
        try:
            return uploaded_file.read().decode("utf-8", errors="ignore")
        except Exception as e:
            return f"[Could not read file: {e}]"


def _quick_insights(text: str) -> dict:
    """Lightweight heuristic extraction — used only as supporting context for the AI prompt."""
    area_matches = re.findall(r"(\d{2,6})\s?(?:sq\.?\s?ft|sqft|square feet)", text, flags=re.I)
    cost_matches = re.findall(r"(?:₹|rs\.?|inr)\s?[\d,]{4,}", text, flags=re.I)
    dates = re.findall(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", text)
    clauses = len(re.findall(r"\bclause\b", text, flags=re.I))
    penalty_mentions = len(re.findall(r"\bpenalt(y|ies)\b", text, flags=re.I))
    return {
        "areas_found": area_matches[:10],
        "costs_found": cost_matches[:10],
        "dates_found": dates[:10],
        "clause_mentions": clauses,
        "penalty_mentions": penalty_mentions,
        "word_count": len(text.split()),
    }


def _generate_full_report(text: str, insights: dict) -> str:
    """Asks the AI to write a complete, structured project report (not just a summary)."""
    context_hint = (
        f"(Heuristic scan found: {insights['word_count']} words, "
        f"{len(insights['areas_found'])} area reference(s), "
        f"{len(insights['costs_found'])} cost reference(s), "
        f"{insights['penalty_mentions']} penalty mention(s).)"
    )

    prompt = f"""You are a senior construction project analyst. Read the document below and write a
COMPLETE, WELL-STRUCTURED PROJECT REPORT. Do not just summarize — produce a full report with the
following sections, each as a heading on its own line starting with "## ":

## Project Overview
## Scope of Work
## Cost Analysis
## Timeline & Milestones
## Risk & Penalty Clauses
## Material & Resource Notes
## Recommendations
## Conclusion

Under each heading, write clear, well-organized paragraphs or bullet points (use "- " for bullets).
Be specific and reference actual figures, dates, and clauses found in the document where possible.
If a section has no relevant information in the document, write "Not specified in the document."
under that heading instead of inventing details.

{context_hint}

DOCUMENT TEXT:
{text[:8000]}
"""

    return chat_with_llama(prompt, history=[])


def _parse_report_to_flowables(report_text: str, styles):
    """Converts the AI's '## Heading' / '- bullet' formatted text into ReportLab flowables."""
    from reportlab.platypus import Paragraph, Spacer, ListFlowable, ListItem

    flowables = []
    bullet_buffer = []

    def flush_bullets():
        if bullet_buffer:
            items = [ListItem(Paragraph(b, styles["body"]), leftIndent=10) for b in bullet_buffer]
            flowables.append(ListFlowable(items, bulletType="bullet", start="circle"))
            flowables.append(Spacer(1, 6))
            bullet_buffer.clear()

    for raw_line in report_text.split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("## "):
            flush_bullets()
            flowables.append(Spacer(1, 10))
            flowables.append(Paragraph(line.replace("## ", ""), styles["heading"]))
        elif line.startswith("- ") or line.startswith("• "):
            bullet_buffer.append(line[2:].strip())
        else:
            flush_bullets()
            flowables.append(Paragraph(line, styles["body"]))
            flowables.append(Spacer(1, 4))

    flush_bullets()
    return flowables


def _build_pdf_report(file_name: str, report_text: str) -> bytes:
    """Builds the final PDF entirely from the AI-generated report text."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=20 * mm, bottomMargin=20 * mm,
        leftMargin=18 * mm, rightMargin=18 * mm,
    )

    base_styles = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "TitleCustom", parent=base_styles["Title"],
            textColor=colors.HexColor("#1E293B"), fontSize=20, spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "SubtitleCustom", parent=base_styles["Normal"],
            textColor=colors.HexColor("#F97316"), fontSize=12, spaceAfter=14,
        ),
        "meta": ParagraphStyle(
            "MetaCustom", parent=base_styles["Normal"],
            textColor=colors.HexColor("#475569"), fontSize=9.5, spaceAfter=2,
        ),
        "heading": ParagraphStyle(
            "HeadingCustom", parent=base_styles["Heading2"],
            textColor=colors.HexColor("#1E293B"), fontSize=14,
            spaceBefore=4, spaceAfter=8,
            borderColor=colors.HexColor("#F97316"),
            borderWidth=0, leftIndent=0,
        ),
        "body": ParagraphStyle(
            "BodyCustom", parent=base_styles["Normal"], fontSize=10.5, leading=15,
        ),
    }

    elements = []
    elements.append(Paragraph("Construction Intelligence Hub", styles["title"]))
    elements.append(Paragraph("AI-Generated Project Report", styles["subtitle"]))
    elements.append(Paragraph(f"<b>Source file:</b> {file_name}", styles["meta"]))
    elements.append(Paragraph(
        f"<b>Generated on:</b> {datetime.now().strftime('%d %B %Y, %I:%M %p')}", styles["meta"]
    ))
    elements.append(Spacer(1, 16))

    elements.extend(_parse_report_to_flowables(report_text, styles))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def render():
    st.markdown(
        """<div class="page-header">
        <h1>📄 Document Analyzer</h1>
        <p>Upload contracts, BOQs, tender documents or site reports — AI writes a complete project report and gives you a downloadable PDF.</p>
        </div>""",
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload a construction document", type=["pdf", "docx", "txt"]
    )

    if uploaded_file:
        with st.spinner("Reading document..."):
            text = _extract_text(uploaded_file)

        insights = _quick_insights(text)

        st.markdown('<div class="cih-card">', unsafe_allow_html=True)
        st.subheader("📊 Quick Insights")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="metric-tile"><div class="value">{insights["word_count"]}</div><div class="label">Words</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-tile"><div class="value">{len(insights["areas_found"])}</div><div class="label">Area refs</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-tile"><div class="value">{len(insights["costs_found"])}</div><div class="label">Cost refs</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="metric-tile"><div class="value">{insights["penalty_mentions"]}</div><div class="label">Penalty clauses</div></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="cih-card">', unsafe_allow_html=True)
        st.subheader("🤖 AI Project Report")

        if "full_report" not in st.session_state:
            st.session_state.full_report = ""

        if st.button("Generate Complete AI Report"):
            with st.spinner("AI is writing the full project report... this may take a moment."):
                st.session_state.full_report = _generate_full_report(text, insights)

        if st.session_state.full_report:
            st.markdown(st.session_state.full_report)

            st.markdown("<br>", unsafe_allow_html=True)
            with st.spinner("Preparing PDF..."):
                pdf_bytes = _build_pdf_report(
                    file_name=uploaded_file.name,
                    report_text=st.session_state.full_report,
                )

            st.download_button(
                label="⬇️ Download Complete AI Report (PDF)",
                data=pdf_bytes,
                file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}_AI_Project_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("📃 View extracted raw text"):
            st.text_area("Extracted text", text, height=300)
    else:
        st.info("Upload a PDF, DOCX or TXT construction document to begin analysis.")