import streamlit as st
import io
import json
import zipfile
from utils.styling import page_hero


def make_report_rows(report_type):
    if report_type == "Monthly Cost Analysis":
        return [
            ["Category", "Planned", "Actual", "Variance"],
            ["Materials", "$45,000", "$42,500", "$2,500"],
            ["Labor", "$38,000", "$40,200", "-$2,200"],
            ["Equipment", "$12,500", "$11,900", "$600"],
        ]
    if report_type == "Safety & Compliance Audit":
        return [
            ["Inspection Item", "Status", "Notes"],
            ["Site PPE", "Pass", "All workers compliant"],
            ["Hazard Logs", "Review", "2 open items"],
            ["OSHA Checklist", "Pass", "Minor signage update needed"],
        ]
    return [
        ["Metric", "Target", "Current", "Status"],
        ["Milestones", "12", "10", "On track"],
        ["Delay Days", "0", "3", "Monitor"],
        ["Quality Score", "95%", "92%", "Improving"],
    ]


def make_csv(report_type):
    rows = make_report_rows(report_type)
    output = io.StringIO()
    for row in rows:
        output.write(",".join(str(item).replace(',', ' ') for item in row) + "\n")
    return output.getvalue().encode("utf-8")


def make_json(report_type):
    rows = make_report_rows(report_type)
    headers = rows[0]
    data = [dict(zip(headers, row)) for row in rows[1:]]
    return json.dumps({"report_type": report_type, "data": data}, indent=2).encode("utf-8")


def make_text(report_type):
    rows = make_report_rows(report_type)
    lines = ["\t".join(str(item) for item in row) for row in rows]
    return "\n".join(lines).encode("utf-8")


def make_excel(report_type):
    rows = make_report_rows(report_type)
    html = ["<html><body><table border='1' cellpadding='4'>"]
    for row in rows:
        html.append("<tr>" + "".join(f"<td>{str(item)}</td>" for item in row) + "</tr>")
    html.append("</table></body></html>")
    return "".join(html).encode("utf-8")


def make_pdf(report_type):
    title = f"{report_type}"
    rows = make_report_rows(report_type)
    content_lines = ["   ".join(str(item) for item in row) for row in rows]
    pdf_text = [title, "", *content_lines]
    text_stream = "\n".join(pdf_text)
    encoded = text_stream.encode("latin-1", errors="replace")

    objects = []
    objects.append(b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n")
    objects.append(b"2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n")
    contents = (
        b"BT /F1 12 Tf 50 750 Td (" + title.encode("latin-1") + b") Tj ET\n"
    )
    y = 730
    for line in content_lines:
        safe_line = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        contents += b"BT /F1 10 Tf 50 " + str(y).encode() + b" Td (" + safe_line.encode("latin-1", errors="replace") + b") Tj ET\n"
        y -= 16
    contents_obj = b"4 0 obj<</Length " + str(len(contents)).encode() + b">\nstream\n" + contents + b"endstream\nendobj\n"
    objects.append(b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Resources<</Font<</F1 5 0 R>>>>/Contents 4 0 R>>endobj\n")
    objects.append(contents_obj)
    objects.append(b"5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n")
    xref_start = sum(len(obj) for obj in objects) + len(b"%PDF-1.4\n")
    xref = [b"xref\n0 6\n0000000000 65535 f \n"]
    offset = len(b"%PDF-1.4\n")
    for obj in objects:
        xref.append(f"{offset:010d} 00000 n \n".encode())
        offset += len(obj)
    trailer = b"trailer<</Size 6/Root 1 0 R>>\nstartxref\n" + str(offset).encode() + b"\n%%EOF\n"
    return b"%PDF-1.4\n" + b"".join(objects) + b"".join(xref) + trailer


def create_report_bytes(report_type, file_format):
    if file_format == "PDF":
        return make_pdf(report_type), "application/pdf", "pdf"
    if file_format == "CSV":
        return make_csv(report_type), "text/csv", "csv"
    if file_format == "Excel":
        return make_excel(report_type), "application/vnd.ms-excel", "xls"
    if file_format == "TXT":
        return make_text(report_type), "text/plain", "txt"
    if file_format == "JSON":
        return make_json(report_type), "application/json", "json"
    if file_format == "Word":
        return make_word(report_type), "application/msword", "doc"
    raise ValueError(f"Unsupported file format: {file_format}")


def make_word(report_type):
    text = make_text(report_type).decode("utf-8")
    rtf = "{\\rtf1\\ansi\\deff0\n" + text.replace("\n", "\\par\n") + "\n}"
    return rtf.encode("utf-8")


def make_archive(report_type):
    files = {
        f"{report_type.lower().replace(' ', '_')}.csv": make_csv(report_type),
        f"{report_type.lower().replace(' ', '_')}.txt": make_text(report_type),
        f"{report_type.lower().replace(' ', '_')}.json": make_json(report_type),
        f"{report_type.lower().replace(' ', '_')}.xls": make_excel(report_type),
        f"{report_type.lower().replace(' ', '_')}.doc": make_word(report_type),
        f"{report_type.lower().replace(' ', '_')}.pdf": make_pdf(report_type),
    }
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buffer.getvalue()


def render():
    page_hero(
        "📄", "Export Project Reports",
        "Generate, Package, and Export Construction Site Analytics &amp; Executive Audits",
        badge="REPORTING SUITE"
    )

    st.markdown("""
        <div class="hub-card" style="padding: 16px 20px; margin-bottom: 18px;">
            <h4>⚙️ Report Export Configuration</h4>
            <span class="hub-card-tag">Choose a report type and preferred export format</span>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        report_type = st.selectbox(
            "📋 Select Report Type",
            ["Monthly Cost Analysis", "Safety & Compliance Audit", "Full Site Progress Summary"],
            help="Choose the analytical domain to include in the generated report bundle."
        )

        if report_type == "Monthly Cost Analysis":
            st.markdown("""
                <div class="hub-strip" style="border-left-color:#00E5FF;">
                    <p style="margin:0;">💰 Includes budget variances, daily burn rates, labor allocations, and forecast projections.</p>
                </div>
            """, unsafe_allow_html=True)
        elif report_type == "Safety & Compliance Audit":
            st.markdown("""
                <div class="hub-strip" style="border-left-color:#00E676;">
                    <p style="margin:0;">🦺 Includes computer vision PPE compliance scores, hazard logs, and OSHA audit checks.</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="hub-strip" style="border-left-color:#FFAB00;">
                    <p style="margin:0;">📊 Comprehensive bundle containing schedule milestone tracking, delays, and executive telemetry.</p>
                </div>
            """, unsafe_allow_html=True)

    with col2:
        file_format = st.radio(
            "📂 Export Format",
            ["PDF", "CSV", "Excel", "TXT", "JSON", "Word", "All Files"],
            horizontal=True,
            help="Select preferred output file format."
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
        bytes_data = None
        mime_type = "application/octet-stream"
        file_name = report_type.lower().replace(' ', '_')

        if file_format == "All Files":
            bytes_data = make_archive(report_type)
            mime_type = "application/zip"
            file_name += ".zip"
        else:
            bytes_data, mime_type, extension = create_report_bytes(report_type, file_format)
            file_name += f".{extension}"

        st.markdown("<hr class='hub-divider'>", unsafe_allow_html=True)
        st.markdown("""
            <div class="hub-card" style="text-align: center; border-color: rgba(0,229,255,0.4); margin-bottom: 20px;">
                <span style="color: #00E5FF; font-weight: 700;">✅ Report Successfully Generated!</span>
                <p class="hub-card-body">Your document bundle is ready for immediate download.</p>
            </div>
        """, unsafe_allow_html=True)

        st.download_button(
            label=f"📥 Download {report_type} ({display_format})",
            data=bytes_data,
            file_name=file_name,
            mime=mime_type,
            width="stretch"
        )
