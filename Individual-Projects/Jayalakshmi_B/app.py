import base64
import io
import json
import random
import re
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ai.ollama_client import build_project_context, chat as ai_chat, extract_text_from_upload, is_construction_related
from ai.prompts import CHATBOT_PROMPT, DOCUMENT_ANALYSIS_PROMPT, REPORT_PROMPT, RISK_PROMPT, SYSTEM_PROMPT

# ------------------- AI Utilities (with fallback) -------------------
def ask_llm(prompt, system_prompt="You are a professional AI Construction Engineer and Project Management Assistant.", context=None):
    """Reusable AI service: call Ollama with a prompt."""
    return ai_chat(prompt, system_prompt=system_prompt, context=context)

# ----- Text extraction functions (with EasyOCR fallback) -----
def extract_text_from_pdf(file_bytes):
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception:
        return ""


def extract_text_from_image(file_bytes):
    """Try Tesseract first, then EasyOCR as fallback."""
    text = ""
    try:
        from PIL import Image
        import pytesseract
        image = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(image)
        if text.strip():
            return text
    except Exception:
        pass
    # Fallback: EasyOCR
    try:
        import easyocr
        reader = easyocr.Reader(['en'], gpu=False)
        image = Image.open(io.BytesIO(file_bytes))
        result = reader.readtext(image, paragraph=True)
        text = "\n".join([item[1] for item in result])
        return text
    except Exception:
        return ""


def extract_text_from_uploaded_file(uploaded_file):
    return extract_text_from_upload(uploaded_file)

# ----- Floor plan parser (generic) -----
def parse_floor_plan_text(text):
    """Extract room names, dimensions, compute area and room counts."""
    # Try multiple patterns
    patterns = [
        re.compile(r'(?P<name>[\w\s]+?)\s*(?P<width>[\d.]+)\s*[xX]\s*(?P<length>[\d.]+)\s*[\'"]?', re.IGNORECASE),
        re.compile(r'(?P<width>[\d.]+)\s*[\'"]?\s*[xX]\s*(?P<length>[\d.]+)\s*[\'"]?\s*(?P<name>[\w\s]+)', re.IGNORECASE),
        re.compile(r'(?P<width>[\d.]+)\s*[xX]\s*(?P<length>[\d.]+)\s*[\'"]?\s*(?P<name>[\w\s]+)', re.IGNORECASE)
    ]
    rooms = []
    total_sqft = 0
    for pattern in patterns:
        for match in pattern.finditer(text):
            if 'name' in match.groupdict() and 'width' in match.groupdict() and 'length' in match.groupdict():
                name = match.group('name').strip()
                width = float(match.group('width'))
                length = float(match.group('length'))
                area = width * length
                total_sqft += area
                rooms.append({'name': name, 'width_ft': width, 'length_ft': length, 'area_sqft': round(area, 2)})
        if rooms:
            break

    # Room type classification (generic)
    room_types = {
        'bedroom': ['bedroom', 'master', 'guest', 'kids', 'children', 'dorm'],
        'bathroom': ['bath', 'toilet', 'washroom', 'restroom', 'bathroom'],
        'kitchen': ['kitchen', 'kitchenette'],
        'living': ['living', 'family', 'great room', 'hall', 'lobby'],
        'dining': ['dining', 'dining room'],
        'balcony': ['balcony', 'patio', 'deck', 'terrace', 'sitout', 'verandah'],
        'closet': ['closet', 'wardrobe', 'storage'],
        'hallway': ['hallway', 'corridor', 'foyer', 'passage', 'entrance'],
        'laundry': ['laundry', 'utility'],
        'garage': ['garage'],
        'office': ['office', 'study', 'den'],
        'store': ['store', 'shop', 'retail']
    }
    counts = {k: 0 for k in room_types}
    for room in rooms:
        name_lower = room['name'].lower()
        matched = False
        for rtype, keywords in room_types.items():
            if any(kw in name_lower for kw in keywords):
                counts[rtype] += 1
                matched = True
                break
        if not matched:
            counts['other'] = counts.get('other', 0) + 1
    counts['total_sqft'] = round(total_sqft, 2)
    counts['rooms'] = rooms
    bhk = counts.get('bedroom', 0)
    counts['BHK'] = f"{bhk} BHK" if bhk > 0 else "Undetermined"
    # Features (generic detection)
    features = {
        'staircase': bool(re.search(r'stair|step', text, re.I)),
        'parking': bool(re.search(r'parking|car|garage', text, re.I)),
        'elevator': bool(re.search(r'elevator|lift', text, re.I)),
        'emergency_exit': bool(re.search(r'emergency\s*exit|fire\s*exit', text, re.I))
    }
    counts['features'] = features
    return counts

# ----- Estimators -----
def estimate_materials(total_sqft):
    cement_kg = total_sqft * 1.8
    steel_kg = total_sqft * 0.12
    sand_cum = total_sqft * 0.02
    aggregate_cum = total_sqft * 0.03
    bricks_units = total_sqft * 6
    paint_litres = total_sqft * 0.14
    return {
        'Cement (kg)': round(cement_kg, 2),
        'Steel (kg)': round(steel_kg, 2),
        'Sand (cum)': round(sand_cum, 2),
        'Aggregate (cum)': round(aggregate_cum, 2),
        'Bricks (units)': round(bricks_units),
        'Paint (litres)': round(paint_litres, 2)
    }

def estimate_costs(total_sqft):
    base_cost = total_sqft * 2200
    gst = base_cost * 0.18
    contingency = base_cost * 0.05
    total_cost = base_cost + gst + contingency
    return {
        'Base Cost': round(base_cost, 2),
        'GST (18%)': round(gst, 2),
        'Contingency (5%)': round(contingency, 2),
        'Total Estimated Cost': round(total_cost, 2)
    }

def estimate_duration(total_sqft, num_rooms):
    months = max(1.0, round((total_sqft / 600.0) + (num_rooms * 0.4), 1))
    return months

def get_project_manager(project_id):
    managers = st.session_state.managers
    row = managers[managers["Project ID"] == project_id]
    return row.iloc[0]["Name"] if not row.empty else "Unassigned"


def get_project_context(project_id):
    projects = get_projects()
    row = projects[projects["Project ID"] == project_id]
    if row.empty:
        return None
    return row.iloc[0].to_dict()


def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def calculate_project_estimates(project_row, extracted_text=""):
    plot_area = safe_float(project_row.get("Plot Area (sqm)", 0))
    floors = int(project_row.get("Floors", 1) or 1)
    missing_info = []
    if plot_area <= 0:
        missing_info.append("Plot size")

    if plot_area > 0:
        cement_kg = plot_area * 0.55 * floors
        steel_kg = plot_area * 0.18 * floors
        bricks_units = int(plot_area * 6)
        sand_cum = plot_area * 0.04
        aggregate_cum = plot_area * 0.05
        concrete_cum = plot_area * 0.06
        paint_litres = plot_area * 0.12
        tiles_sqft = plot_area * 0.8
    else:
        cement_kg = steel_kg = bricks_units = sand_cum = aggregate_cum = concrete_cum = paint_litres = tiles_sqft = 0

    material_cost = cement_kg * 9 + steel_kg * 0.8 + bricks_units * 0.08 + sand_cum * 1800 + aggregate_cum * 1600 + concrete_cum * 4200 + paint_litres * 140 + tiles_sqft * 45
    labour_cost = plot_area * 2500
    equipment_cost = plot_area * 500
    electrical_cost = plot_area * 320
    plumbing_cost = plot_area * 280
    finishing_cost = plot_area * 650
    misc_cost = plot_area * 180

    durations = {
        "foundation_duration": max(4, round(plot_area / 200, 1)),
        "structural_work": max(5, round(plot_area / 180, 1)),
        "brick_work": max(4, round(plot_area / 240, 1)),
        "roofing": max(3, round(plot_area / 300, 1)),
        "electrical": max(2, round(plot_area / 400, 1)),
        "plumbing": max(2, round(plot_area / 420, 1)),
        "finishing": max(4, round(plot_area / 220, 1)),
    }
    durations["total_project_duration"] = round(sum(durations.values()) / 30 + 1, 1)

    return {
        "project_name": project_row.get("Project Name", ""),
        "project_type": project_row.get("Building Type", ""),
        "classification": "Residential",
        "material_estimates": {
            "Cement (kg)": round(cement_kg, 2),
            "Steel (kg)": round(steel_kg, 2),
            "Bricks (units)": int(bricks_units),
            "Sand (cum)": round(sand_cum, 2),
            "Aggregate (cum)": round(aggregate_cum, 2),
            "Concrete (cum)": round(concrete_cum, 2),
            "Paint (litres)": round(paint_litres, 2),
            "Tiles (sqft)": round(tiles_sqft, 2),
        },
        "cost_estimates": {
            "Material Cost": round(material_cost, 2),
            "Labour Cost": round(labour_cost, 2),
            "Equipment Cost": round(equipment_cost, 2),
            "Electrical Cost": round(electrical_cost, 2),
            "Plumbing Cost": round(plumbing_cost, 2),
            "Finishing Cost": round(finishing_cost, 2),
            "Miscellaneous Cost": round(misc_cost, 2),
        },
        "duration_estimates": durations,
        "missing_information": missing_info,
        "document_excerpt": (extracted_text or "")[:2500],
    }


def extract_json_payload(response):
    try:
        start = response.find("{")
        end = response.rfind("}")
        if start >= 0 and end > start:
            return json.loads(response[start:end+1])
    except Exception:
        pass
    return None


def analyze_uploaded_document(uploaded_file, project_id):
    project_row = get_project_context(project_id)
    if project_row is None:
        return {"error": "Project not found."}

    extracted_text, error = extract_text_from_upload(uploaded_file)
    if error:
        return {"error": error}

    if not is_construction_related(extracted_text):
        return {"error": "I am designed only for construction-related assistance. Please ask a question related to construction, project management, site safety, blueprints, materials, cost estimation, or documents."}

    if error:
        return {"error": error}

    estimates = calculate_project_estimates(project_row, extracted_text)
    context = build_project_context(project_row)
    context["document_text"] = extracted_text[:5000]
    context["calculated_estimates"] = estimates

    llm_prompt = (
        f"Document Text:\n{extracted_text[:5000]}\n\n"
        f"Project Context:\n{json.dumps(context, indent=2)}\n\n"
        "Return a concise JSON object with project_name, project_type, building_type, classification, "
        "building_details, area_analysis, missing_information, executive_summary, design_suggestions and recommendations."
    )
    llm_response = ai_chat(llm_prompt, system_prompt=SYSTEM_PROMPT + "\n" + DOCUMENT_ANALYSIS_PROMPT, context=context)
    parsed_response = extract_json_payload(llm_response)

    if parsed_response:
        estimates.update(parsed_response)
    else:
        estimates["llm_summary"] = llm_response

    if not estimates.get("missing_information"):
        estimates["missing_information"] = ["Please provide the drawing scale, dimensions or plot size for accurate estimation."] if not estimates.get("area_analysis") else []

    return estimates


def analyze_project_risks(project_id):
    project_row = get_project_context(project_id)
    if project_row is None:
        return {"risks": [], "risk_score": 0}

    context = build_project_context(project_row)
    context["calculated_estimates"] = calculate_project_estimates(project_row)
    llm_prompt = f"Project Context:\n{json.dumps(context, indent=2)}\n\nAnalyze budget, schedule, material, labour, supplier, equipment, quality and safety risk."
    llm_response = ai_chat(llm_prompt, system_prompt=SYSTEM_PROMPT + "\n" + RISK_PROMPT, context=context)
    parsed_response = extract_json_payload(llm_response)
    if isinstance(parsed_response, dict) and isinstance(parsed_response.get("risks"), list):
        return parsed_response
    if isinstance(parsed_response, list):
        return {"risks": parsed_response, "risk_score": 55}
    return {"risks": [{"name": "No risks detected", "severity": "Low", "cause": "No data", "impact": "No impact", "recommendation": "Continue monitoring", "priority": "Low"}], "risk_score": 15}


def generate_daily_report(project_id):
    project_row = get_project_context(project_id)
    if project_row is None:
        return "No project context available."

    context = build_project_context(project_row)
    context.update({
        "attendance_summary": "Attendance recorded for the current shift.",
        "completed_tasks": ["Site clearance", "Foundation inspection"],
        "pending_tasks": ["Structural steel fix", "Material delivery follow-up"],
        "project_progress": project_row.get("Current Progress", 0),
        "material_consumption": "Cement and steel consumption logged.",
        "equipment_usage": "Excavator and mixer in active use.",
        "risks": ["Material delivery delay", "Weather disruption"],
        "recommendations": ["Escalate procurement", "Increase safety brief"],
        "tomorrow_work_plan": ["Continue structural work", "Inspect reinforcement"],
    })
    prompt = f"Project Context:\n{json.dumps(context, indent=2)}\n\nGenerate a professional daily construction report."
    return ai_chat(prompt, system_prompt=SYSTEM_PROMPT + "\n" + REPORT_PROMPT, context=context)


def answer_project_chat(project_id, user_message):
    if not user_message or not user_message.strip():
        return "Please enter a question."
    if not is_construction_related(user_message):
        return "I am designed only for construction-related assistance. Please ask a question related to construction, project management, site safety, blueprints, materials, cost estimation, or documents."
    context = None
    if project_id:
        project_row = get_project_context(project_id)
        if project_row is None:
            return "Selected project context is not available."
        context = build_project_context(project_row)
    return ai_chat(user_message, system_prompt=CHATBOT_PROMPT, context=context)


def build_pdf_bytes(text):
    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.splitlines():
        pdf.multi_cell(0, 8, line)
    return pdf.output(dest="S").encode("latin-1")


def select_available_staff(required_engineers=2, required_workers=10):
    eng = st.session_state.engineers
    wrk = st.session_state.workers
    available_engineers = eng[eng["Assigned Project"] == "None"].head(required_engineers)
    if len(available_engineers) < required_engineers:
        available_engineers = eng.head(required_engineers)
    available_workers = wrk[wrk["Assigned Project"] == "None"].head(required_workers)
    if len(available_workers) < required_workers:
        available_workers = wrk.head(required_workers)
    return available_engineers, available_workers

# ------------------- Page Config -------------------
st.set_page_config(page_title="Construction Intelligence Hub", layout="wide", initial_sidebar_state="expanded")

# ------------------- Custom CSS & Theme -------------------
def get_background_css():
    image_path = Path(__file__).with_name("construction pic.png")
    if not image_path.exists():
        return ""
    encoded_image = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    return f'''
    .stApp {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.78), rgba(255, 255, 255, 0.78)), url("data:image/png;base64,{encoded_image}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        min-height: 100vh;
    }}
    '''

def apply_theme():
    dark_mode = st.session_state.get("dark_mode", False)
    if dark_mode:
        bg_color = "#010b14"
        text_color = "#0F74D8"
        card_bg = "#100101"
        border_color = "#0d0d0e"
        header_bg = "#e9ecef"
        accent = "#4a9eff"
        sidebar_bg = "#79b0eb"
        sidebar_text = "#212529"
        nav_border = "rgba(255,255,255,0.08)"
        overlay_color = "rgba(20, 20, 20, 0.78)"
    else:
        bg_color = "#f8f9fa"
        text_color = "#212529"
        card_bg = "#ffffff"
        border_color = "#dee2e6"
        header_bg = "#e9ecef"
        accent = "#0066cc"
        sidebar_bg = "#79b0eb"
        sidebar_text = "#fbfefffb"
        nav_border = "rgba(0,0,0,0.08)"
        overlay_color = "rgba(255, 255, 255, 0.78)"
    st.markdown(f"""
    <style>
        {get_background_css()}
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
        .stApp::after {{
            content: "";
            position: fixed;
            inset: 0;
            z-index: -1;
            background: {overlay_color};
            pointer-events: none;
        }}
        .stApp * {{
            color: {text_color} !important;
        }}
        .stApp header {{
            background-color: {header_bg};
        }}
        h1, h2, h3, h4, h5, h6, .stMarkdown, .stText, .stMetric, .stDataFrame {{
            color: {text_color} !important;
        }}
        div[data-testid="stMetric"] {{
            background-color: {card_bg};
            border: 1px solid {border_color};
            border-radius: 12px;
            padding: 18px;
            box-shadow: 0 6px 14px rgba(0,0,0,0.06);
            transition: transform 0.28s cubic-bezier(.2,.8,.2,1), box-shadow 0.28s, border-color 0.28s;
            transform-origin: center;
            will-change: transform;
        }}
        div[data-testid="stMetric"]:hover {{
            transform: translateY(-10px) rotateX(4deg) scale(1.02);
            box-shadow: 0 26px 60px rgba(0,0,0,0.35), 0 0 28px {accent}33;
            border-color: {accent};
        }}
        .hero-card {{
            margin: 1.5rem auto 1rem auto;
            max-width: 900px;
            padding: 2.2rem 2rem;
            text-align: center;
            border-radius: 24px;
            background: linear-gradient(135deg, rgba(0, 102, 204, 0.12), rgba(121, 176, 235, 0.16));
            border: 1px solid rgba(0, 102, 204, 0.18);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08);
        }}
        .hero-badge {{
            display: inline-block;
            padding: 0.35rem 0.8rem;
            border-radius: 999px;
            background: {accent};
            color: white;
            font-weight: 700;
            font-size: 0.9rem;
            margin-bottom: 0.9rem;
        }}
        .hero-title {{
            font-size: 2.5rem;
            font-weight: 800;
            margin: 0 0 0.45rem 0;
            color: {text_color};
        }}
        .hero-subtitle {{
            font-size: 1.08rem;
            margin: 0;
            color: {text_color};
            opacity: 0.9;
        }}
        .login-card {{
            max-width: 460px;
            margin: 1rem auto 0 auto;
            padding: 1.25rem 1.3rem;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid rgba(0, 0, 0, 0.08);
            box-shadow: 0 10px 24px rgba(0, 0, 0, 0.08);
        }}
        .stButton > button {{
            background-color: {accent};
            color: white;
            border-radius: 8px;
            border: none;
            padding: 0.5rem 1.5rem;
            transition: 0.3s;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stButton > button:hover {{
            background-color: {accent}cc;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        .stSelectbox, .stTextInput, .stNumberInput {{
            background-color: {card_bg};
            border-radius: 8px;
        }}
        .stSidebar {{
            background-color: {sidebar_bg};
            color: {sidebar_text};
            border-right: 1px solid {border_color};
            padding-top: 1rem;
        }}
        .stSidebar * {{ color: {sidebar_text} !important; }}
        div[role="radiogroup"] input[type="radio"] {{
            display: none !important;
        }}
        div[role="radiogroup"] > label {{
            display: flex;
            align-items: center;
            padding: 12px 14px;
            margin: 8px 10px;
            border-radius: 12px;
            background-color: transparent;
            border: 1px solid {nav_border};
            color: {sidebar_text};
            cursor: pointer;
            transition: transform 0.18s ease, box-shadow 0.18s ease, background-color 0.18s ease;
        }}
        div[role="radiogroup"] > label[aria-checked="true"] {{
            background-color: {accent} !important;
            color: #ffffff !important;
            box-shadow: 0 6px 18px rgba(0,0,0,0.45), 0 0 18px {accent}33;
            border: 1px solid {accent};
        }}
        div[role="radiogroup"] > label:hover {{
            transform: translateY(-6px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.22);
        }}
        div[role="radiogroup"] > label::before {{
            content: "📊";
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 34px;
            height: 34px;
            margin-right: 12px;
            border-radius: 8px;
            background: rgba(255,255,255,0.04);
            font-size: 18px;
        }}
        div[role="radiogroup"] > label:nth-child(1)::before {{ content: "📊"; }}
        div[role="radiogroup"] > label:nth-child(2)::before {{ content: "📁"; }}
        div[role="radiogroup"] > label:nth-child(3)::before {{ content: "📦"; }}
        div[role="radiogroup"] > label:nth-child(4)::before {{ content: "👷"; }}
        div[role="radiogroup"] > label:nth-child(5)::before {{ content: "🤖"; }}
        div[role="radiogroup"] > label:nth-child(6)::before {{ content: "📈"; }}
        div[role="radiogroup"] > label:nth-child(7)::before {{ content: "📑"; }}
        div[role="radiogroup"] > label:nth-child(8)::before {{ content: "ℹ️"; }}
        .stDataFrame {{
            background-color: {card_bg};
            border-radius: 8px;
            border: 1px solid {border_color};
        }}
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {{
            color: {text_color};
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: {card_bg};
            border-radius: 8px 8px 0 0;
            border: 1px solid {border_color};
            border-bottom: none;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: {accent} !important;
            color: white !important;
        }}
        .stProgress > div > div {{
            background-color: {accent};
        }}
        .stAlert {{
            background-color: {card_bg};
            border-left: 5px solid {accent};
            color: {text_color};
        }}
    </style>
    """, unsafe_allow_html=True)

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
apply_theme()

# ------------------- Sample Data Generation -------------------
def generate_sample_data():
    random.seed(42)
    np.random.seed(42)

    def random_date(start, end):
        return start + timedelta(days=random.randint(0, (end - start).days))

    client_names = ["ABC Constructions", "XYZ Developers", "PQR Group", "LMN Infra", "RST Housing",
                    "UVW Builders", "MNO Estates", "DEF Projects", "GHI Realty", "JKL Ventures"]
    clients = pd.DataFrame({
        "Client ID": [f"C{str(i).zfill(3)}" for i in range(1, 11)],
        "Name": client_names,
        "Contact": [f"+91-9{random.randint(10000000,99999999)}" for _ in range(10)],
        "Email": [f"{name.replace(' ', '').lower()}@gmail.com" for name in client_names]
    })

    contractors = ["Sharma Constructions", "Verma Builders", "Patel Infra", "Singh Developers", "Kumar Enterprises",
                   "Gupta Constructions", "Joshi Builders", "Rana Projects", "Thakur Infra", "Yadav Developers"]
    contractors = pd.DataFrame({
        "Contractor ID": [f"CON{str(i).zfill(3)}" for i in range(1, 11)],
        "Name": contractors,
        "Contact": [f"+91-9{random.randint(10000000,99999999)}" for _ in range(10)]
    })

    suppliers = []
    for i in range(1, 31):
        suppliers.append({
            "Supplier ID": f"S{str(i).zfill(3)}",
            "Company Name": f"Supplier {i}",
            "Contact": f"+91-9{random.randint(10000000,99999999)}",
            "Materials": random.choice(["Cement, Steel", "Sand, Aggregate", "Bricks, Tiles", "Paint, Electrical", "Plumbing, HVAC"]),
            "Rating": round(random.uniform(3.0, 5.0), 1),
            "Payment Status": random.choice(["Paid", "Pending", "Partial"])
        })
    suppliers = pd.DataFrame(suppliers)

    stages = ["Planning", "Excavation", "Foundation", "Superstructure", "Finishing", "Handover"]
    statuses = ["Not Started", "In Progress", "On Hold", "Completed", "Delayed"]
    building_types = ["Apartment", "Villa", "Office Tower", "Warehouse", "School", "Hospital", "Mall", "Hotel"]
    project_names = [f"Project {chr(65+i)}" for i in range(50)]
    projects = []
    for i in range(1, 51):
        client = clients.iloc[random.randint(0,9)]
        contractor = contractors.iloc[random.randint(0,9)]
        start = random_date(datetime(2023,1,1), datetime(2024,12,1))
        duration = random.randint(180, 720)
        end = start + timedelta(days=duration)
        progress = random.randint(0, 100)
        budget = random.randint(50, 500) * 100000
        stage = random.choice(stages)
        status = random.choice(statuses)
        if progress > 80:
            status = "Completed"
        elif progress < 20 and status == "Completed":
            status = "In Progress"
        projects.append({
            "Project ID": f"P{str(i).zfill(3)}",
            "Project Name": project_names[i-1],
            "Client": client["Name"],
            "Client ID": client["Client ID"],
            "Contractor": contractor["Name"],
            "Location": f"City {random.randint(1,20)}",
            "Building Type": random.choice(building_types),
            "Plot Area (sqm)": random.randint(200, 5000),
            "Floors": random.randint(1, 20),
            "Budget": budget,
            "Start Date": start.strftime("%Y-%m-%d"),
            "Completion Date": end.strftime("%Y-%m-%d"),
            "Current Progress": progress,
            "Current Stage": stage,
            "Status": status,
        })
    projects = pd.DataFrame(projects)

    engineers = []
    for i in range(1, 41):
        proj = projects.iloc[random.randint(0,49)] if random.random() > 0.2 else None
        engineers.append({
            "Engineer ID": f"E{str(i).zfill(3)}",
            "Name": f"Engr. {random.choice(['Amit','Ravi','Priya','Sneha','Vikram','Anita','Rahul','Neha','Suresh','Kavya'])} {chr(65+i%26)}",
            "Experience (years)": random.randint(2, 25),
            "Assigned Project": proj["Project Name"] if proj is not None else "None",
            "Project ID": proj["Project ID"] if proj is not None else "",
            "Role": random.choice(["Site Engineer", "Structural Engineer", "QA/QC Engineer", "Planning Engineer"]),
            "Attendance (%)": random.randint(70, 100),
            "Safety Score": round(random.uniform(70, 100), 1)
        })
    engineers = pd.DataFrame(engineers)

    managers = []
    for i in range(1, 21):
        proj = projects.iloc[random.randint(0,49)] if random.random() > 0.3 else None
        managers.append({
            "Manager ID": f"M{str(i).zfill(3)}",
            "Name": f"PM {random.choice(['Sunil','Deepak','Meera','Rohit','Anjali'])} {chr(65+i%26)}",
            "Experience (years)": random.randint(5, 30),
            "Assigned Project": proj["Project Name"] if proj is not None else "None",
            "Project ID": proj["Project ID"] if proj is not None else "",
            "Performance Rating": round(random.uniform(3.0, 5.0), 1)
        })
    managers = pd.DataFrame(managers)

    workers = []
    for i in range(1, 101):
        proj = projects.iloc[random.randint(0,49)] if random.random() > 0.1 else None
        workers.append({
            "Worker ID": f"W{str(i).zfill(3)}",
            "Name": f"Worker {random.choice(['Kumar','Singh','Patel','Sharma','Verma','Yadav'])} {chr(65+i%26)}",
            "Role": random.choice(["Mason", "Carpenter", "Electrician", "Plumber", "Painter", "Helper", "Operator"]),
            "Assigned Project": proj["Project Name"] if proj is not None else "None",
            "Project ID": proj["Project ID"] if proj is not None else "",
            "Attendance (%)": random.randint(60, 100),
            "Safety Score": round(random.uniform(50, 100), 1)
        })
    workers = pd.DataFrame(workers)

    material_names = ["Cement (50kg)", "Steel (TMT)", "Sand (ton)", "Aggregate (ton)", "Bricks (1000 units)",
                      "Tiles (sqm)", "Paint (litre)", "Plumbing pipes (m)", "Electrical wire (m)", "Wood (cft)"]
    materials = []
    for i, name in enumerate(material_names):
        stock = random.randint(100, 5000)
        reserved = random.randint(0, int(stock*0.3))
        materials.append({
            "Material ID": f"MAT{str(i+1).zfill(3)}",
            "Material Name": name,
            "Current Stock": stock,
            "Reserved Quantity": reserved,
            "Available Quantity": stock - reserved,
            "Unit": random.choice(["kg", "ton", "cum", "sqm", "litre", "m", "units"]),
            "Supplier": suppliers.iloc[random.randint(0,29)]["Company Name"],
            "Warehouse": random.choice(["Main Store", "Site Store A", "Site Store B"]),
            "Delivery Status": random.choice(["In Stock", "Partial", "Out of Stock"])
        })
    materials = pd.DataFrame(materials)

    purchase_orders = []
    for i in range(1, 501):
        mat = materials.iloc[random.randint(0,len(materials)-1)]
        proj = projects.iloc[random.randint(0,49)]
        qty = random.randint(10, 500)
        unit_price = round(random.uniform(10, 5000), 2)
        purchase_orders.append({
            "PO ID": f"PO{str(i).zfill(4)}",
            "Project": proj["Project Name"],
            "Project ID": proj["Project ID"],
            "Material": mat["Material Name"],
            "Quantity": qty,
            "Unit": mat["Unit"],
            "Unit Price": unit_price,
            "Total": qty * unit_price,
            "Supplier": mat["Supplier"],
            "Order Date": random_date(datetime(2024,1,1), datetime(2025,6,1)).strftime("%Y-%m-%d"),
            "Delivery Date": random_date(datetime(2025,1,1), datetime(2025,12,1)).strftime("%Y-%m-%d"),
            "Status": random.choice(["Ordered", "Shipped", "Delivered", "Cancelled"])
        })
    purchase_orders = pd.DataFrame(purchase_orders)

    equipment_names = ["Excavator", "Crane", "Concrete Mixer", "Bulldozer", "Dump Truck", "Scaffolding", "Generators", "Compactor"]
    equipment = []
    for i in range(1, 101):
        proj = projects.iloc[random.randint(0,49)] if random.random() > 0.3 else None
        equipment.append({
            "Equipment ID": f"EQ{str(i).zfill(3)}",
            "Name": random.choice(equipment_names),
            "Model": f"Model {chr(65+random.randint(0,25))}{random.randint(100,999)}",
            "Availability": random.choice(["Available", "In Use", "Under Maintenance"]),
            "Current Project": proj["Project Name"] if proj is not None else "None",
            "Project ID": proj["Project ID"] if proj is not None else "",
            "Operator": f"Op {random.randint(1,20)}",
            "Maintenance Status": random.choice(["Good", "Needs Service", "Major Repair"])
        })
    equipment = pd.DataFrame(equipment)

    daily_reports = []
    for i in range(1, 501):
        proj = projects.iloc[random.randint(0,49)]
        date = random_date(datetime(2024,1,1), datetime(2025,6,1))
        daily_reports.append({
            "Report ID": f"DR{str(i).zfill(4)}",
            "Project ID": proj["Project ID"],
            "Project Name": proj["Project Name"],
            "Date": date.strftime("%Y-%m-%d"),
            "Progress": random.randint(0,100),
            "Labour Count": random.randint(5, 100),
            "Material Used": random.choice(["Cement 100 bags", "Steel 2 tons", "Bricks 500", "Sand 5 tons"]),
            "Remarks": random.choice(["Work in progress", "Weather delay", "Material shortage", "Good progress"]),
            "Safety Incidents": random.randint(0,2)
        })
    daily_reports = pd.DataFrame(daily_reports)

    documents = []
    for i in range(1, 301):
        proj = projects.iloc[random.randint(0,49)]
        doc_types = ["BOQ", "Drawing", "Contract", "Report", "Permit", "Specification", "Invoice"]
        documents.append({
            "Document ID": f"DOC{str(i).zfill(4)}",
            "Project ID": proj["Project ID"],
            "Project Name": proj["Project Name"],
            "Title": f"{random.choice(doc_types)} {i}",
            "Type": random.choice(doc_types),
            "Upload Date": random_date(datetime(2024,1,1), datetime(2025,6,1)).strftime("%Y-%m-%d"),
            "Version": f"v{random.randint(1,5)}"
        })
    documents = pd.DataFrame(documents)

    cost_items = ["Foundation", "Excavation", "PCC", "Footings", "RCC Columns", "RCC Beams", "RCC Slabs",
                  "Brickwork", "Roofing", "Plastering", "Flooring", "Painting", "Doors", "Windows",
                  "Electrical", "Plumbing", "HVAC", "Fire Safety", "Labour", "Equipment",
                  "Transportation", "Contingency", "Taxes"]
    cost_breakdown = []
    for _, proj in projects.iterrows():
        total_budget = proj["Budget"]
        for item in cost_items:
            amount = round(random.uniform(0.01, 0.08) * total_budget, 2)
            qty = random.randint(1, 500)
            unit_price = round(amount / qty, 2) if qty > 0 else 0
            status = random.choice(["Pending", "In Progress", "Completed"])
            cost_breakdown.append({
                "Project ID": proj["Project ID"],
                "Project Name": proj["Project Name"],
                "Item": item,
                "Quantity": qty,
                "Unit": random.choice(["kg", "ton", "cum", "sqm", "litre", "m", "units"]),
                "Unit Price": unit_price,
                "Total Cost": amount,
                "Status": status
            })
    cost_breakdown = pd.DataFrame(cost_breakdown)

    safety_quality = []
    for _, proj in projects.iterrows():
        safety_quality.append({
            "Project ID": proj["Project ID"],
            "Project Name": proj["Project Name"],
            "PPE Compliance (%)": random.randint(60,100),
            "Safety Inspections": random.randint(0,10),
            "Incidents": random.randint(0,3),
            "Safety Score": round(random.uniform(60,100),1),
            "Concrete Quality": random.choice(["Good","Average","Poor"]),
            "Brickwork Quality": random.choice(["Good","Average","Poor"]),
            "Plaster Quality": random.choice(["Good","Average","Poor"]),
            "Finishing Quality": random.choice(["Good","Average","Poor"])
        })
    safety_quality = pd.DataFrame(safety_quality)

    budget_util = []
    for _, proj in projects.iterrows():
        spent = random.uniform(0.1, 1.1) * proj["Budget"] * (proj["Current Progress"]/100)
        budget_util.append({
            "Project ID": proj["Project ID"],
            "Project Name": proj["Project Name"],
            "Allocated": proj["Budget"],
            "Spent": round(min(spent, proj["Budget"]), 2),
            "Remaining": round(max(proj["Budget"] - spent, 0), 2)
        })
    budget_util = pd.DataFrame(budget_util)

    milestones = []
    for _, proj in projects.iterrows():
        start = datetime.strptime(proj["Start Date"], "%Y-%m-%d")
        end = datetime.strptime(proj["Completion Date"], "%Y-%m-%d")
        total_days = (end - start).days
        for i, stage in enumerate(stages):
            m_start = start + timedelta(days=int(total_days * i / len(stages)))
            m_end = start + timedelta(days=int(total_days * (i+1) / len(stages)))
            completed = "Completed" if random.random() < 0.7 else "Pending"
            milestones.append({
                "Project ID": proj["Project ID"],
                "Project Name": proj["Project Name"],
                "Stage": stage,
                "Start": m_start.strftime("%Y-%m-%d"),
                "End": m_end.strftime("%Y-%m-%d"),
                "Status": completed
            })
    milestones = pd.DataFrame(milestones)

    return {
        "clients": clients,
        "contractors": contractors,
        "suppliers": suppliers,
        "projects": projects,
        "engineers": engineers,
        "managers": managers,
        "workers": workers,
        "materials": materials,
        "purchase_orders": purchase_orders,
        "equipment": equipment,
        "daily_reports": daily_reports,
        "documents": documents,
        "cost_breakdown": cost_breakdown,
        "safety_quality": safety_quality,
        "budget_util": budget_util,
        "milestones": milestones
    }

@st.cache_data
def load_data():
    return generate_sample_data()

# ------------------- Load Data into Session State -------------------
def init_session_data():
    if "data_loaded" not in st.session_state:
        data = load_data()
        for key, df in data.items():
            st.session_state[key] = df
        st.session_state.data_loaded = True

init_session_data()

def get_projects():
    return st.session_state.projects

def get_workers():
    return st.session_state.workers

def get_suppliers():
    return st.session_state.suppliers

# ------------------- Session State for UI -------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "selected_project_id" not in st.session_state:
    st.session_state.selected_project_id = None
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "edit_project_id" not in st.session_state:
    st.session_state.edit_project_id = None
if "edit_worker_id" not in st.session_state:
    st.session_state.edit_worker_id = None
if "show_add_project" not in st.session_state:
    st.session_state.show_add_project = False
if "show_add_worker" not in st.session_state:
    st.session_state.show_add_worker = False
if "ai_document_analysis" not in st.session_state:
    st.session_state.ai_document_analysis = None
if "ai_chat_response" not in st.session_state:
    st.session_state.ai_chat_response = None
if "ai_risk_analysis" not in st.session_state:
    st.session_state.ai_risk_analysis = None
if "daily_report_content" not in st.session_state:
    st.session_state.daily_report_content = None

# ------------------- Login / Logout -------------------
def login():
    st.markdown("""
    <div class="hero-card">
        <div class="hero-badge">AI-powered Construction Platform</div>
        <h1 class="hero-title">Construction Intelligence Hub</h1>
        <p class="hero-subtitle">A modern web application built with Streamlit for smarter project planning, monitoring, and collaboration.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div class="login-card">
            <h3 style="margin-bottom: 0.2rem;">Welcome back</h3>
            <p style="margin-top: 0; color: #5b6472;">Choose your role to continue</p>
        </div>
        """, unsafe_allow_html=True)
        role = st.selectbox("Select Role", ["Admin", "Project Manager", "Site Engineer", "Client"], key="login_role")
        if st.button("Login", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.role = role
            st.session_state.selected_project_id = None
            if role == "Client":
                assigned_proj = get_projects().sample(1).iloc[0]["Project ID"]
                st.session_state.client_project_id = assigned_proj
            st.rerun()

def logout():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.selected_project_id = None
    st.rerun()

# ------------------- Page Functions -------------------
def about_page():
    st.title("ℹ️ About Construction Intelligence Hub")
    st.markdown("""
    ### Vision
    **Construction Intelligence Hub** is an AI-powered platform designed to streamline construction project management, enhance collaboration, and provide intelligent decision support for civil engineers and project stakeholders.

    ### Version
    **Milestone 2** – Full AI integration with Ollama Llama 3.2.

    ### Technology Stack
    - **Frontend:** Streamlit
    - **Language:** Python
    - **Data:** Pandas, CSV (in-memory)
    - **Visualization:** Plotly
    - **AI:** Ollama (Llama 3.2) – optional, with fallback

    ### Features
    - Role-based access (Admin, PM, Engineer, Client)
    - Project management with add/edit
    - Resource Management (Workforce, Equipment, Material & Cost Estimation, Supplier Monitoring, Inventory)
    - AI Document/Floor Plan Analyzer with room detection and missing info prompts
    - Project Q&A Chatbot
    - Daily Report with auto-fill and PDF export
    - AI Risk Detection (Budget, Schedule, Materials, Suppliers, Equipment, Labour, Quality, Safety)
    - Site Safety Monitoring (image upload with AI advice)
    - AI Report Generator (Weekly, Monthly, Executive, etc.)
    - Dark/Light mode toggle

    ### Contact
    For support or inquiries, reach us at: **support@constructionhub.ai**
    """)
    st.divider()
    st.caption("© 2026 Construction Intelligence Hub. All rights reserved.")

def dashboard_page():
    st.title("📊 Dashboard")
    st.markdown("### Company-wide Overview")
    projects = get_projects()
    budget_util = st.session_state.budget_util
    engineers = st.session_state.engineers
    workers = get_workers()
    materials = st.session_state.materials

    col1, col2, col3, col4 = st.columns(4)
    total_projects = len(projects)
    active_projects = len(projects[projects["Status"] == "In Progress"])
    completed = len(projects[projects["Status"] == "Completed"])
    delayed = len(projects[projects["Status"] == "Delayed"])
    col1.metric("Total Projects", total_projects)
    col2.metric("Active Projects", active_projects)
    col3.metric("Completed", completed)
    col4.metric("Delayed", delayed, delta="-" if delayed>0 else "+")

    col1, col2, col3, col4 = st.columns(4)
    total_budget = projects["Budget"].sum()
    spent = budget_util["Spent"].sum()
    col1.metric("Total Budget", f"₹{total_budget:,.0f}")
    col2.metric("Budget Utilized", f"₹{spent:,.0f}", delta=f"{spent/total_budget*100:.1f}%")
    total_engineers = len(engineers)
    total_workers = len(workers)
    col3.metric("Engineers", total_engineers)
    col4.metric("Workers", total_workers)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Project Status")
        status_counts = projects["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig = px.pie(status_counts, values="Count", names="Status", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Budget vs Spent by Project (Top 10)")
        top10 = budget_util.sort_values("Allocated", ascending=False).head(10)
        fig = px.bar(top10, x="Project Name", y=["Allocated", "Spent"], barmode="group",
                     labels={"value":"Amount (₹)", "variable":"Type"})
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Project Progress Distribution")
        progress_bins = pd.cut(projects["Current Progress"], bins=[0,20,40,60,80,100], labels=["0-20","20-40","40-60","60-80","80-100"])
        progress_counts = progress_bins.value_counts().reset_index()
        progress_counts.columns = ["Progress Range", "Count"]
        fig = px.bar(progress_counts, x="Progress Range", y="Count", color="Progress Range")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Material Stock Status")
        stock_status = materials["Delivery Status"].value_counts().reset_index()
        stock_status.columns = ["Status", "Count"]
        fig = px.pie(stock_status, values="Count", names="Status")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("AI Insights")
    st.info("🔍 **AI Analysis:** Based on current data, 3 projects are at risk of delay due to material shortages. Recommend expediting procurement for Project P012, P034, P045.")
    st.info("📈 **Cost Saving Opportunity:** Switching to alternative supplier for cement could reduce costs by 5-8% across all projects.")
    st.info("⚠️ **Safety Alert:** Project P023 has had 2 safety incidents this month. Review safety protocols.")

# ----- Project Management (unchanged) -----
def project_management_page():
    st.title("📋 Project Management")
    projects = get_projects()
    search = st.text_input("🔍 Search by name or ID", "")
    if search:
        filtered = projects[projects["Project Name"].str.contains(search, case=False) | 
                            projects["Project ID"].str.contains(search, case=False)]
    else:
        filtered = projects
    st.dataframe(filtered[["Project ID", "Project Name", "Client", "Status", "Current Progress", "Budget"]], 
                 use_container_width=True, height=400)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Add New Project"):
            st.session_state.show_add_project = not st.session_state.show_add_project
            if st.session_state.show_add_project:
                st.session_state.edit_project_id = None
    with col2:
        project_options = ["Select a project"] + projects["Project ID"].tolist()
        selected = st.selectbox("Edit project", project_options, index=0)
        if selected != "Select a project":
            st.session_state.edit_project_id = selected
            st.session_state.show_add_project = False

    if st.session_state.show_add_project:
        with st.expander("Add New Project", expanded=True):
            with st.form("add_project_form"):
                cols = st.columns(2)
                with cols[0]:
                    new_name = st.text_input("Project Name")
                    new_client = st.text_input("Client")
                    new_contractor = st.text_input("Contractor")
                    new_location = st.text_input("Location")
                    new_building_type = st.selectbox("Building Type", ["Apartment", "Villa", "Office Tower", "Warehouse", "School", "Hospital", "Mall", "Hotel"])
                    new_plot_area = st.number_input("Plot Area (sqm)", min_value=1, value=500)
                    new_floors = st.number_input("Floors", min_value=1, value=5)
                with cols[1]:
                    new_budget = st.number_input("Budget (₹)", min_value=10000, value=5000000, step=100000)
                    new_start = st.date_input("Start Date", value=datetime.today())
                    new_completion = st.date_input("Completion Date", value=datetime.today() + timedelta(days=365))
                    new_stage = st.selectbox("Current Stage", ["Planning", "Excavation", "Foundation", "Superstructure", "Finishing", "Handover"])
                    new_status = st.selectbox("Status", ["Not Started", "In Progress", "On Hold", "Completed", "Delayed"])
                    new_progress = st.slider("Progress (%)", 0, 100, 0)
                submitted = st.form_submit_button("Add Project")
                if submitted:
                    if not new_name:
                        st.error("Project Name is required")
                    else:
                        max_id = max([int(p.split("P")[1]) for p in projects["Project ID"]]) if len(projects) > 0 else 0
                        new_id = f"P{str(max_id+1).zfill(3)}"
                        new_row = {
                            "Project ID": new_id,
                            "Project Name": new_name,
                            "Client": new_client,
                            "Client ID": "",
                            "Contractor": new_contractor,
                            "Location": new_location,
                            "Building Type": new_building_type,
                            "Plot Area (sqm)": new_plot_area,
                            "Floors": new_floors,
                            "Budget": new_budget,
                            "Start Date": new_start.strftime("%Y-%m-%d"),
                            "Completion Date": new_completion.strftime("%Y-%m-%d"),
                            "Current Progress": new_progress,
                            "Current Stage": new_stage,
                            "Status": new_status,
                        }
                        st.session_state.projects = pd.concat([projects, pd.DataFrame([new_row])], ignore_index=True)
                        budget_util = st.session_state.budget_util
                        new_budget_row = {
                            "Project ID": new_id,
                            "Project Name": new_name,
                            "Allocated": new_budget,
                            "Spent": 0,
                            "Remaining": new_budget
                        }
                        st.session_state.budget_util = pd.concat([budget_util, pd.DataFrame([new_budget_row])], ignore_index=True)
                        cost_breakdown = st.session_state.cost_breakdown
                        for item in ["Foundation", "Superstructure", "Finishing"]:
                            cost_breakdown = pd.concat([cost_breakdown, pd.DataFrame([{
                                "Project ID": new_id,
                                "Project Name": new_name,
                                "Item": item,
                                "Quantity": 0,
                                "Unit": "units",
                                "Unit Price": 0,
                                "Total Cost": 0,
                                "Status": "Pending"
                            }])], ignore_index=True)
                        st.session_state.cost_breakdown = cost_breakdown
                        st.success(f"Project {new_name} added successfully!")
                        st.session_state.show_add_project = False
                        st.rerun()

    if st.session_state.edit_project_id:
        proj = projects[projects["Project ID"] == st.session_state.edit_project_id].iloc[0]
        with st.expander(f"Edit Project {proj['Project Name']}", expanded=True):
            with st.form("edit_project_form"):
                cols = st.columns(2)
                with cols[0]:
                    edit_name = st.text_input("Project Name", value=proj["Project Name"])
                    edit_client = st.text_input("Client", value=proj["Client"])
                    edit_contractor = st.text_input("Contractor", value=proj["Contractor"])
                    edit_location = st.text_input("Location", value=proj["Location"])
                    edit_building_type = st.selectbox("Building Type", ["Apartment", "Villa", "Office Tower", "Warehouse", "School", "Hospital", "Mall", "Hotel"], index=["Apartment", "Villa", "Office Tower", "Warehouse", "School", "Hospital", "Mall", "Hotel"].index(proj["Building Type"]))
                    edit_plot_area = st.number_input("Plot Area (sqm)", min_value=1, value=int(proj["Plot Area (sqm)"]))
                    edit_floors = st.number_input("Floors", min_value=1, value=int(proj["Floors"]))
                with cols[1]:
                    edit_budget = st.number_input("Budget (₹)", min_value=10000, value=int(proj["Budget"]), step=100000)
                    edit_start = st.date_input("Start Date", value=datetime.strptime(proj["Start Date"], "%Y-%m-%d"))
                    edit_completion = st.date_input("Completion Date", value=datetime.strptime(proj["Completion Date"], "%Y-%m-%d"))
                    edit_stage = st.selectbox("Current Stage", ["Planning", "Excavation", "Foundation", "Superstructure", "Finishing", "Handover"], index=["Planning", "Excavation", "Foundation", "Superstructure", "Finishing", "Handover"].index(proj["Current Stage"]))
                    edit_status = st.selectbox("Status", ["Not Started", "In Progress", "On Hold", "Completed", "Delayed"], index=["Not Started", "In Progress", "On Hold", "Completed", "Delayed"].index(proj["Status"]))
                    edit_progress = st.slider("Progress (%)", 0, 100, int(proj["Current Progress"]))
                submitted = st.form_submit_button("Update Project")
                if submitted:
                    idx = projects[projects["Project ID"] == st.session_state.edit_project_id].index[0]
                    st.session_state.projects.at[idx, "Project Name"] = edit_name
                    st.session_state.projects.at[idx, "Client"] = edit_client
                    st.session_state.projects.at[idx, "Contractor"] = edit_contractor
                    st.session_state.projects.at[idx, "Location"] = edit_location
                    st.session_state.projects.at[idx, "Building Type"] = edit_building_type
                    st.session_state.projects.at[idx, "Plot Area (sqm)"] = edit_plot_area
                    st.session_state.projects.at[idx, "Floors"] = edit_floors
                    st.session_state.projects.at[idx, "Budget"] = edit_budget
                    st.session_state.projects.at[idx, "Start Date"] = edit_start.strftime("%Y-%m-%d")
                    st.session_state.projects.at[idx, "Completion Date"] = edit_completion.strftime("%Y-%m-%d")
                    st.session_state.projects.at[idx, "Current Stage"] = edit_stage
                    st.session_state.projects.at[idx, "Status"] = edit_status
                    st.session_state.projects.at[idx, "Current Progress"] = edit_progress
                    b_idx = st.session_state.budget_util[st.session_state.budget_util["Project ID"] == st.session_state.edit_project_id].index[0]
                    st.session_state.budget_util.at[b_idx, "Allocated"] = edit_budget
                    st.success("Project updated successfully!")
                    st.session_state.edit_project_id = None
                    st.rerun()

    if len(filtered) > 0:
        selected_id = st.selectbox("Select Project ID to view details", filtered["Project ID"].tolist(), key="detail_select")
        if selected_id:
            show_project_detail(selected_id)

def show_project_detail(project_id):
    projects = get_projects()
    proj = projects[projects["Project ID"] == project_id].iloc[0]
    st.divider()
    st.header(f"📌 {proj['Project Name']} ({proj['Project ID']})")
    tabs = st.tabs(["Overview", "Progress", "Timeline", "Budget", "Cost Breakdown", "Team", "Documents", "Photos", "AI Insights"])
    with tabs[0]:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Client:** {proj['Client']}")
            st.markdown(f"**Contractor:** {proj['Contractor']}")
            st.markdown(f"**Location:** {proj['Location']}")
            st.markdown(f"**Building Type:** {proj['Building Type']}")
        with col2:
            st.markdown(f"**Floors:** {proj['Floors']}")
            st.markdown(f"**Plot Area:** {proj['Plot Area (sqm)']} sqm")
            st.markdown(f"**Status:** {proj['Status']}")
            st.markdown(f"**Current Stage:** {proj['Current Stage']}")
        st.markdown(f"**Budget:** ₹{proj['Budget']:,.2f}")
        st.markdown(f"**Start:** {proj['Start Date']}  |  **Completion:** {proj['Completion Date']}")
        st.progress(proj['Current Progress']/100, text=f"Progress: {proj['Current Progress']}%")
    with tabs[1]:
        st.subheader("Progress History")
        dates = pd.date_range(start=proj['Start Date'], end=datetime.today(), periods=10)
        progress_vals = np.linspace(0, proj['Current Progress'], len(dates))
        history_df = pd.DataFrame({"Date": dates, "Progress": progress_vals})
        fig = px.line(history_df, x="Date", y="Progress", title="Progress Over Time")
        st.plotly_chart(fig, use_container_width=True)
        st.subheader("Stage Completion")
        milestones = st.session_state.milestones
        stage_data = milestones[milestones["Project ID"] == project_id]
        if not stage_data.empty:
            st.dataframe(stage_data[["Stage", "Start", "End", "Status"]], use_container_width=True)
        else:
            st.info("No milestones available")
    with tabs[2]:
        st.subheader("Project Timeline")
        milestones = st.session_state.milestones
        m_data = milestones[milestones["Project ID"] == project_id]
        if not m_data.empty:
            fig = px.timeline(m_data, x_start="Start", x_end="End", y="Stage", color="Status", title="Milestones")
            fig.update_yaxes(categoryorder="array", categoryarray=["Planning","Excavation","Foundation","Superstructure","Finishing","Handover"])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No timeline data")
    with tabs[3]:
        st.subheader("Budget Overview")
        budget_util = st.session_state.budget_util
        bud = budget_util[budget_util["Project ID"] == project_id].iloc[0]
        col1, col2, col3 = st.columns(3)
        col1.metric("Allocated", f"₹{bud['Allocated']:,.2f}")
        col2.metric("Spent", f"₹{bud['Spent']:,.2f}")
        col3.metric("Remaining", f"₹{bud['Remaining']:,.2f}")
        fig = go.Figure(data=[go.Pie(labels=['Spent', 'Remaining'], values=[bud['Spent'], bud['Remaining']], hole=0.4)])
        st.plotly_chart(fig, use_container_width=True)
    with tabs[4]:
        st.subheader("Detailed Cost Breakdown")
        cost_breakdown = st.session_state.cost_breakdown
        breakdown = cost_breakdown[cost_breakdown["Project ID"] == project_id]
        if not breakdown.empty:
            st.dataframe(breakdown[["Item", "Quantity", "Unit", "Unit Price", "Total Cost", "Status"]], use_container_width=True)
            total = breakdown["Total Cost"].sum()
            st.metric("Total Estimated Cost", f"₹{total:,.2f}")
        else:
            st.info("No breakdown data")
    with tabs[5]:
        st.subheader("Assigned Team")
        engineers = st.session_state.engineers
        managers = st.session_state.managers
        workers = get_workers()
        engs = engineers[engineers["Project ID"] == project_id]
        if not engs.empty:
            st.write("**Engineers:**")
            st.dataframe(engs[["Name", "Role", "Experience (years)", "Attendance (%)", "Safety Score"]], use_container_width=True)
        mgrs = managers[managers["Project ID"] == project_id]
        if not mgrs.empty:
            st.write("**Project Managers:**")
            st.dataframe(mgrs[["Name", "Experience (years)", "Performance Rating"]], use_container_width=True)
        wrks = workers[workers["Project ID"] == project_id]
        if not wrks.empty:
            st.write("**Workers:**")
            st.dataframe(wrks[["Name", "Role", "Attendance (%)", "Safety Score"]], use_container_width=True)
    with tabs[6]:
        st.subheader("Project Documents")
        documents = st.session_state.documents
        docs = documents[documents["Project ID"] == project_id]
        if not docs.empty:
            st.dataframe(docs[["Title", "Type", "Upload Date", "Version"]], use_container_width=True)
        else:
            st.info("No documents")
    with tabs[7]:
        st.subheader("Site Photos")
        # Simulate images with placeholders
        cols = st.columns(3)
        for i in range(3):
            with cols[i]:
                st.image(f"https://picsum.photos/seed/{project_id}_{i}/400/300", caption=f"Photo {i+1}")
    with tabs[8]:
        st.subheader("AI Insights")
        st.caption("Use the built-in AI tools to analyze uploaded drawings, ask project questions, review risks, and generate a daily site report.")

        uploaded_file = st.file_uploader("Upload drawing or document", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"], key=f"ai_upload_{project_id}")
        if uploaded_file is not None:
            if st.button("Analyze Document", key=f"analyze_doc_{project_id}"):
                with st.spinner("Analyzing the uploaded document with Llama 3.2..."):
                    st.session_state.ai_document_analysis = analyze_uploaded_document(uploaded_file, project_id)
                st.success("Document analysis completed")

        if st.session_state.ai_document_analysis:
            analysis = st.session_state.ai_document_analysis
            if analysis.get("error"):
                st.error(analysis["error"])
            else:
                st.write("**Executive Summary**")
                st.write(analysis.get("executive_summary") or analysis.get("llm_summary", "No summary available."))
                col1, col2, col3 = st.columns(3)
                col1.metric("Project Name", analysis.get("project_name", "-"))
                col2.metric("Classification", analysis.get("classification", "-"))
                col3.metric("Building Type", analysis.get("building_type", "-"))
                with st.expander("Material Estimation"):
                    st.json(analysis.get("material_estimates", {}))
                with st.expander("Cost Estimation"):
                    st.json(analysis.get("cost_estimates", {}))
                with st.expander("Duration Estimation"):
                    st.json(analysis.get("duration_estimates", {}))
                with st.expander("Missing Information"):
                    st.write(analysis.get("missing_information", []))
                with st.expander("Design Suggestions"):
                    st.write(analysis.get("design_suggestions", []))
                with st.expander("Recommendations"):
                    st.write(analysis.get("recommendations", []))

        st.divider()
        st.subheader("AI Construction Assistant")
        assistant_prompt = st.text_area("Ask about the project", key=f"assistant_prompt_{project_id}", placeholder="Example: How much cement is required? What is the estimated cost? Explain this drawing.")
        if st.button("Ask Assistant", key=f"assistant_btn_{project_id}") and assistant_prompt.strip():
            with st.spinner("Preparing the answer..."):
                st.session_state.ai_chat_response = answer_project_chat(project_id, assistant_prompt)
        if st.session_state.ai_chat_response:
            st.markdown(st.session_state.ai_chat_response)

        st.divider()
        st.subheader("AI Risk Analysis")
        if st.button("Run Risk Analysis", key=f"risk_btn_{project_id}"):
            with st.spinner("Reviewing the project risks..."):
                st.session_state.ai_risk_analysis = analyze_project_risks(project_id)
        if st.session_state.ai_risk_analysis:
            risk_df = pd.DataFrame(st.session_state.ai_risk_analysis.get("risks", []))
            if not risk_df.empty:
                st.metric("Overall Risk Score", f"{st.session_state.ai_risk_analysis.get('risk_score', 0)}/100")
                st.dataframe(risk_df, use_container_width=True)

        st.divider()
        st.subheader("Daily Construction Report")
        if st.button("Generate Daily Report", key=f"daily_report_btn_{project_id}"):
            with st.spinner("Generating the report..."):
                st.session_state.daily_report_content = generate_daily_report(project_id)
        if st.session_state.daily_report_content:
            st.text_area("Generated Report", st.session_state.daily_report_content, height=260, key=f"daily_report_text_{project_id}")
            st.download_button("Download PDF", data=build_pdf_bytes(st.session_state.daily_report_content), file_name=f"{project_id}_daily_report.pdf", mime="application/pdf", key=f"pdf_{project_id}")
            st.download_button("Download Text", data=st.session_state.daily_report_content, file_name=f"{project_id}_daily_report.txt", key=f"txt_{project_id}")

def client_portal_page():
    st.title("👤 Client Portal")
    if "client_project_id" in st.session_state:
        proj_id = st.session_state.client_project_id
        proj = get_projects()[get_projects()["Project ID"] == proj_id]
        if not proj.empty:
            st.success(f"Accessing project: {proj.iloc[0]['Project Name']}")
            show_project_detail(proj_id)
        else:
            st.warning("No project assigned to you.")
    else:
        st.warning("Please contact admin to assign a project.")

# ===================== RESOURCE MANAGEMENT (restructured) =====================
def resource_management_page():
    st.title("📦 Resource Management")

    tabs = st.tabs([
        "Materials", 
        "Purchase Orders", 
        "Suppliers", 
        "Warehouse", 
        "Equipment", 
        "Material Estimation", 
        "Cost Estimation", 
        "Supplier Monitoring"

    ])

    # ----- 0. Materials -----
    with tabs[0]:
        st.subheader("Central Material Inventory")
        materials = st.session_state.materials
        st.dataframe(materials, use_container_width=True)
        fig = px.bar(materials, x="Material Name", y=["Current Stock", "Reserved Quantity"], 
                     barmode="group", title="Stock vs Reserved")
        st.plotly_chart(fig, use_container_width=True)
        st.subheader("Material Requirements by Project (sample)")
        projects = get_projects()
        req = []
        for _, proj in projects.sample(5).iterrows():
            for _, mat in materials.sample(3).iterrows():
                req.append({
                    "Project": proj["Project Name"],
                    "Material": mat["Material Name"],
                    "Required": random.randint(10,200),
                    "Available": mat["Available Quantity"],
                    "Status": "Sufficient" if mat["Available Quantity"] > random.randint(10,200) else "Shortage"
                })
        req_df = pd.DataFrame(req)
        st.dataframe(req_df, use_container_width=True)

    # ----- 1. Purchase Orders -----
    with tabs[1]:
        st.subheader("Purchase Orders")
        purchase_orders = st.session_state.purchase_orders
        st.dataframe(purchase_orders, use_container_width=True)
        col1, col2, col3 = st.columns(3)
        col1.metric("Total POs", len(purchase_orders))
        col2.metric("Delivered", len(purchase_orders[purchase_orders["Status"]=="Delivered"]))
        col3.metric("Pending", len(purchase_orders[purchase_orders["Status"]!="Delivered"]))

    # ----- 2. Suppliers -----
    with tabs[2]:
        st.subheader("Supplier Management")
        suppliers = get_suppliers()
        st.dataframe(suppliers, use_container_width=True)

    # ----- 3. Warehouse -----
    with tabs[3]:
        st.subheader("Warehouse Utilization")
        warehouses = ["Main Store", "Site Store A", "Site Store B"]
        usage = [random.randint(30,90) for _ in warehouses]
        fig = px.bar(x=warehouses, y=usage, labels={"x":"Warehouse", "y":"Utilization (%)"}, title="Warehouse Utilization")
        st.plotly_chart(fig, use_container_width=True)

    # ----- 4. Equipment -----
    with tabs[4]:
        st.subheader("⚙️ Equipment Management")
        equipment = st.session_state.equipment
        st.dataframe(equipment[["Name", "Model", "Availability", "Current Project", "Maintenance Status"]], use_container_width=True)
        avail_counts = equipment["Availability"].value_counts().reset_index()
        avail_counts.columns = ["Availability", "Count"]
        fig = px.pie(avail_counts, values="Count", names="Availability", title="Equipment Availability")
        st.plotly_chart(fig, use_container_width=True)
        maint_counts = equipment["Maintenance Status"].value_counts().reset_index()
        maint_counts.columns = ["Status", "Count"]
        fig2 = px.bar(maint_counts, x="Status", y="Count", title="Maintenance Status")
        st.plotly_chart(fig2, use_container_width=True)

    # ----- 5. Material Estimation -----
    with tabs[5]:
        st.subheader("Material Estimation Calculator")
        col1, col2 = st.columns(2)
        with col1:
            area = st.number_input("Total Built-up Area (sqm)", min_value=1, value=100)
            floors = st.number_input("Number of Floors", min_value=1, value=2)
            wall_height = st.number_input("Wall Height (m)", value=3.0)
        with col2:
            concrete_grade = st.selectbox("Concrete Grade", ["M20", "M25", "M30"])
            steel_grade = st.selectbox("Steel Grade", ["Fe415", "Fe500"])
        
        if st.button("Estimate Materials"):
            # Simple estimation formulas (approximate)
            cement_kg = area * floors * 200  # rough
            steel_kg = area * floors * 80
            sand_cum = area * floors * 0.5
            aggregate_cum = area * floors * 0.8
            bricks_units = area * floors * 500
            paint_litres = area * floors * 0.2
            st.subheader("Estimated Quantities")
            st.write(f"**Cement:** {cement_kg:.0f} kg  (~{cement_kg/50:.0f} bags)")
            st.write(f"**Steel:** {steel_kg:.0f} kg")
            st.write(f"**Sand:** {sand_cum:.2f} cum")
            st.write(f"**Aggregate:** {aggregate_cum:.2f} cum")
            st.write(f"**Bricks:** {bricks_units:.0f} units")
            st.write(f"**Paint:** {paint_litres:.2f} litres")


    # ----- 6. Cost Estimation -----
    with tabs[6]:
        st.subheader("💰 Cost Estimation")
        item_costs = {
            "Cement (per bag)": 400,
            "Steel (per kg)": 70,
            "Sand (per cum)": 1500,
            "Aggregate (per cum)": 1200,
            "Bricks (per 1000)": 7000,
            "Labour (per sqm)": 500,
            "Equipment (lump sum)": 100000,
        }
        qty_inputs = {}
        col1, col2 = st.columns(2)
        with col1:
            qty_inputs["Cement (per bag)"] = st.number_input("Cement bags", value=100)
            qty_inputs["Steel (per kg)"] = st.number_input("Steel kg", value=500)
            qty_inputs["Sand (per cum)"] = st.number_input("Sand cum", value=10)
            qty_inputs["Aggregate (per cum)"] = st.number_input("Aggregate cum", value=15)
        with col2:
            qty_inputs["Bricks (per 1000)"] = st.number_input("Bricks (1000 units)", value=20)
            qty_inputs["Labour (per sqm)"] = st.number_input("Labour sqm", value=200)
            qty_inputs["Equipment (lump sum)"] = st.number_input("Equipment cost", value=100000)
        if st.button("Calculate Total Cost"):
            total = 0
            breakdown = []
            for item, qty in qty_inputs.items():
                if qty > 0:
                    unit_price = item_costs.get(item, 0)
                    cost = qty * unit_price
                    total += cost
                    breakdown.append({"Item": item, "Quantity": qty, "Unit Price": unit_price, "Cost": cost})
            gst = total * 0.18
            contingency = total * 0.05
            final_total = total + gst + contingency
            st.subheader("Cost Breakdown")
            bd = pd.DataFrame(breakdown)
            st.dataframe(bd, use_container_width=True)
            st.write(f"**Subtotal:** ₹{total:,.2f}")
            st.write(f"**GST (18%):** ₹{gst:,.2f}")
            st.write(f"**Contingency (5%):** ₹{contingency:,.2f}")
            st.success(f"**Total Estimated Cost:** ₹{final_total:,.2f}")
            with st.spinner("Generating cost insights..."):
                prompt = f"Explain the cost breakdown: subtotal {total}, GST {gst}, contingency {contingency}, final {final_total}. Suggest cost-saving opportunities and highlight high-cost activities."
                advice = ask_llm(prompt)
            st.info("💡 **AI Cost Advice**")
            st.markdown(advice)

    # ----- 7. Supplier Monitoring -----
    with tabs[7]:
        st.subheader("📦 Supplier Monitoring")
        purchase_orders = st.session_state.purchase_orders
        suppliers = get_suppliers()
        if not purchase_orders.empty:
            delayed = purchase_orders[purchase_orders["Status"] == "Delayed"] if "Delayed" in purchase_orders["Status"].values else purchase_orders[purchase_orders["Status"] == "Cancelled"]
            st.write(f"**Delayed/Cancelled Orders:** {len(delayed)}")
            if not delayed.empty:
                st.dataframe(delayed[["PO ID", "Project", "Material", "Supplier", "Order Date", "Delivery Date", "Status"]], use_container_width=True)
            if st.button("Get Supplier Performance Analysis"):
                with st.spinner("Analyzing suppliers..."):
                    prompt = f"""
                    Analyze the following supplier data and order history:
                    Suppliers: {suppliers[['Company Name', 'Rating', 'Payment Status']].to_dict()}
                    Purchase Orders: {purchase_orders[['PO ID', 'Supplier', 'Material', 'Quantity', 'Status']].head(10).to_dict()}
                    Identify high-performing suppliers, delay risks, and recommend alternative suppliers if needed.
                    """
                    analysis = ask_llm(prompt)
                st.info(analysis)
        else:
            st.info("No purchase orders available.")

    # ----- 7. Inventory -----
    with tabs[7]:
        st.subheader("📊 Inventory Management")
        materials = st.session_state.materials
        st.dataframe(materials[["Material Name", "Current Stock", "Available Quantity", "Unit", "Delivery Status"]], use_container_width=True)
        low_stock = materials[materials["Available Quantity"] < 50]
        if not low_stock.empty:
            st.warning("⚠️ Low Stock Alert")
            st.dataframe(low_stock[["Material Name", "Available Quantity", "Unit"]], use_container_width=True)
            if st.button("Get Reorder Suggestions"):
                prompt = f"Based on current inventory: {low_stock[['Material Name', 'Available Quantity']].to_dict()}, suggest reorder quantities and priorities."
                with st.spinner("Generating suggestions..."):
                    rec = ask_llm(prompt)
                st.info(rec)
        else:
            st.success("All materials are adequately stocked.")

# ----- Workforce Page (unchanged) -----
def workforce_page():
    st.title("👷 Workforce Management")
    workers = get_workers()
    engineers = st.session_state.engineers
    managers = st.session_state.managers
    role_filter = st.selectbox("Filter by Role", ["All", "Engineer", "Project Manager", "Worker"])
    if role_filter == "Engineer":
        df = engineers.copy()
        df["Role"] = df["Role"].apply(lambda x: "Engineer")
    elif role_filter == "Project Manager":
        df = managers.copy()
        df["Role"] = "Project Manager"
    elif role_filter == "Worker":
        df = workers.copy()
        df["Role"] = df["Role"].apply(lambda x: "Worker")
    else:
        eng = engineers.copy()
        eng["Role"] = "Engineer"
        mgr = managers.copy()
        mgr["Role"] = "Project Manager"
        wrk = workers.copy()
        wrk["Role"] = "Worker"
        df = pd.concat([eng, mgr, wrk], ignore_index=True)
    cols = ["Name", "Role", "Assigned Project", "Attendance (%)", "Safety Score"] if "Safety Score" in df.columns else ["Name", "Role", "Assigned Project", "Performance Rating"] if "Performance Rating" in df.columns else ["Name", "Role", "Assigned Project", "Attendance (%)"]
    st.dataframe(df[cols], use_container_width=True)
    total = len(df)
    assigned = len(df[df["Assigned Project"] != "None"])
    st.metric("Total Personnel", total)
    st.metric("Assigned to Projects", assigned)

    st.subheader("Manage Workers")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Add New Worker"):
            st.session_state.show_add_worker = not st.session_state.show_add_worker
            if st.session_state.show_add_worker:
                st.session_state.edit_worker_id = None
    with col2:
        worker_options = ["Select a worker"] + workers["Worker ID"].tolist()
        selected_worker = st.selectbox("Edit Worker", worker_options, index=0)
        if selected_worker != "Select a worker":
            st.session_state.edit_worker_id = selected_worker
            st.session_state.show_add_worker = False

    if st.session_state.show_add_worker:
        with st.expander("Add New Worker", expanded=True):
            with st.form("add_worker_form"):
                cols = st.columns(2)
                with cols[0]:
                    w_name = st.text_input("Worker Name")
                    w_role = st.selectbox("Role", ["Mason", "Carpenter", "Electrician", "Plumber", "Painter", "Helper", "Operator"])
                    w_attendance = st.slider("Attendance (%)", 0, 100, 80)
                with cols[1]:
                    w_project = st.selectbox("Assigned Project", ["None"] + get_projects()["Project Name"].tolist())
                    w_safety = st.slider("Safety Score", 0, 100, 70)
                submitted = st.form_submit_button("Add Worker")
                if submitted:
                    if not w_name:
                        st.error("Worker Name is required")
                    else:
                        max_id = max([int(w.split("W")[1]) for w in workers["Worker ID"]]) if len(workers) > 0 else 0
                        new_id = f"W{str(max_id+1).zfill(3)}"
                        project_id = ""
                        if w_project != "None":
                            project_id = get_projects()[get_projects()["Project Name"] == w_project].iloc[0]["Project ID"]
                        new_row = {
                            "Worker ID": new_id,
                            "Name": w_name,
                            "Role": w_role,
                            "Assigned Project": w_project,
                            "Project ID": project_id,
                            "Attendance (%)": w_attendance,
                            "Safety Score": w_safety
                        }
                        st.session_state.workers = pd.concat([workers, pd.DataFrame([new_row])], ignore_index=True)
                        st.success(f"Worker {w_name} added successfully!")
                        st.session_state.show_add_worker = False
                        st.rerun()

    if st.session_state.edit_worker_id:
        worker = workers[workers["Worker ID"] == st.session_state.edit_worker_id].iloc[0]
        with st.expander(f"Edit Worker {worker['Name']}", expanded=True):
            with st.form("edit_worker_form"):
                cols = st.columns(2)
                with cols[0]:
                    edit_w_name = st.text_input("Worker Name", value=worker["Name"])
                    edit_w_role = st.selectbox("Role", ["Mason", "Carpenter", "Electrician", "Plumber", "Painter", "Helper", "Operator"], index=["Mason", "Carpenter", "Electrician", "Plumber", "Painter", "Helper", "Operator"].index(worker["Role"]))
                    edit_w_attendance = st.slider("Attendance (%)", 0, 100, int(worker["Attendance (%)"]))
                with cols[1]:
                    current_project = worker["Assigned Project"] if worker["Assigned Project"] != "None" else "None"
                    edit_w_project = st.selectbox("Assigned Project", ["None"] + get_projects()["Project Name"].tolist(), index=(["None"] + get_projects()["Project Name"].tolist()).index(current_project))
                    edit_w_safety = st.slider("Safety Score", 0, 100, int(worker["Safety Score"]))
                submitted = st.form_submit_button("Update Worker")
                if submitted:
                    idx = workers[workers["Worker ID"] == st.session_state.edit_worker_id].index[0]
                    st.session_state.workers.at[idx, "Name"] = edit_w_name
                    st.session_state.workers.at[idx, "Role"] = edit_w_role
                    st.session_state.workers.at[idx, "Attendance (%)"] = edit_w_attendance
                    st.session_state.workers.at[idx, "Safety Score"] = edit_w_safety
                    if edit_w_project != "None":
                        st.session_state.workers.at[idx, "Assigned Project"] = edit_w_project
                        st.session_state.workers.at[idx, "Project ID"] = get_projects()[get_projects()["Project Name"] == edit_w_project].iloc[0]["Project ID"]
                    else:
                        st.session_state.workers.at[idx, "Assigned Project"] = "None"
                        st.session_state.workers.at[idx, "Project ID"] = ""
                    st.success("Worker updated successfully!")
                    st.session_state.edit_worker_id = None
                    st.rerun()

# ===================== AI ASSISTANT (with enhanced features) =====================
def ai_assistant_page():
    st.title("🤖 AI Civil Engineering Assistant")
    tabs = st.tabs(["Chat", "Floor Plan Analyzer", "Risk Analysis", "Safety Assistant"])

    # Tab 0: Chat
    with tabs[0]:
        st.subheader("Project Q&A Assistant")
        project_options = ["None"] + get_projects()["Project Name"].tolist()
        selected_project = st.selectbox("Select project for context", project_options)
        user_q = st.text_input("Your question:", placeholder="e.g., What is the construction timeline?")
        if st.button("Ask"):
            if user_q.strip():
                project_id = None
                if selected_project != "None":
                    proj = get_projects()[get_projects()["Project Name"] == selected_project].iloc[0]
                    project_id = proj["Project ID"]
                with st.spinner("Thinking..."):
                    response = answer_project_chat(project_id, user_q)
                st.info(f"🧠 **AI Response:**\n\n{response}")
            else:
                st.warning("Please enter a question.")

    # Tab 1: Floor Plan Analyzer
    with tabs[1]:
        st.subheader("📐 Floor Plan / Blueprint Analyzer")
        project_choice = st.selectbox("Associate with project (optional)", ["None"] + get_projects()["Project Name"].tolist())
        uploaded_plan = st.file_uploader("Upload building sketch, blueprint, or floor plan", type=["png", "jpg", "jpeg", "pdf", "txt"])
        
        user_text = ""
        use_manual = False
        
        if uploaded_plan:
            with st.spinner("Extracting text from image..."):
                text, error = extract_text_from_uploaded_file(uploaded_plan)
                if error:
                    st.warning(error)
                    use_manual = True
                elif not text.strip():
                    st.warning("No text could be extracted from the image. Please enter building details manually below.")
                    use_manual = True
                else:
                    st.success("✅ Text extracted successfully!")
                    user_text = text
                    with st.expander("📄 Extracted Text (preview)"):
                        st.code(text[:1000] + ("..." if len(text)>1000 else ""))
        
        if use_manual:
            st.subheader("📝 Manual Entry")
            st.markdown("Enter building details in the format: `Building Type, Total Area (sqft), Number of Floors`")
            st.markdown("*Example:*\nHospital, 75000, 5\nOffice Building, 45000, 4")
            manual_input = st.text_area("Building details", height=100, placeholder="Hospital, 75000, 5")
            if st.button("Analyze Manual Input"):
                if manual_input.strip():
                    user_text = manual_input
                else:
                    st.error("Please enter building details.")
        
        if user_text and user_text.strip():
            with st.spinner("Analyzing building plan..."):
                # -------- Parse building information (simplified) --------
                # Extract building type, area, and floors from text
                import re
                
                # Try to identify building type from text
                building_type = "Unknown"
                if "hospital" in user_text.lower() or "medical" in user_text.lower() or "clinic" in user_text.lower():
                    building_type = "Hospital"
                elif "school" in user_text.lower() or "college" in user_text.lower() or "university" in user_text.lower():
                    building_type = "School"
                elif "office" in user_text.lower() or "commercial" in user_text.lower():
                    building_type = "Commercial Office"
                elif "residential" in user_text.lower() or "apartment" in user_text.lower() or "villa" in user_text.lower():
                    building_type = "Residential"
                elif "hotel" in user_text.lower() or "resort" in user_text.lower():
                    building_type = "Hotel"
                elif "warehouse" in user_text.lower() or "industrial" in user_text.lower():
                    building_type = "Industrial"
                elif "retail" in user_text.lower() or "mall" in user_text.lower():
                    building_type = "Retail Store"
                elif "parking" in user_text.lower() or "garage" in user_text.lower():
                    building_type = "Parking Structure"
                
                # Extract total area (look for sq ft, sqft, square feet, etc.)
                area_match = re.search(r'(\d+[,.]?\d*)\s*(?:sq\.?\s*ft|sqft|square\s*feet|square\s*foot)', user_text, re.IGNORECASE)
                if area_match:
                    total_area = float(area_match.group(1).replace(',', ''))
                else:
                    # Try to find any large number that might be area
                    numbers = re.findall(r'(\d+[,.]?\d*)', user_text)
                    if numbers:
                        # Assume the largest number might be the area
                        total_area = max([float(n.replace(',', '')) for n in numbers if float(n.replace(',', '')) > 100])
                    else:
                        total_area = 0
                
                # Extract number of floors
                floors_match = re.search(r'(\d+)\s*(?:floors|stories|storeys|levels)', user_text, re.IGNORECASE)
                if floors_match:
                    num_floors = int(floors_match.group(1))
                else:
                    num_floors = 1
                
                # Extract capacity (beds, rooms, etc.)
                capacity_match = re.search(r'(\d+)\s*(?:bed|room|unit|capacity)', user_text, re.IGNORECASE)
                capacity = int(capacity_match.group(1)) if capacity_match else 0
                
                # -------- Display Building Summary --------
                st.markdown("### 🏢 Building Summary")
                col1, col2 = st.columns(2)
                col1.metric("Building Type", building_type)
                col1.metric("Total Area", f"{total_area:,.0f} sqft" if total_area > 0 else "Not detected")
                col2.metric("Number of Floors", num_floors)
                col2.metric("Capacity", f"{capacity} beds" if capacity > 0 else "Not detected")
                
                # -------- Determine construction complexity factor --------
                # Hospitals are more complex than residential
                complexity_factors = {
                    "Hospital": 1.5,
                    "School": 1.2,
                    "Commercial Office": 1.3,
                    "Residential": 1.0,
                    "Hotel": 1.4,
                    "Industrial": 1.1,
                    "Retail Store": 1.2,
                    "Parking Structure": 0.8,
                    "Unknown": 1.0
                }
                complexity = complexity_factors.get(building_type, 1.0)
                
                # -------- Material Estimation --------
                st.subheader("🧱 Material Estimation")
                if total_area > 0:
                    # Adjust material estimates based on building type
                    material_estimates = estimate_materials(total_area * complexity)
                    
                    # For hospitals, add special materials
                    if building_type == "Hospital":
                        material_estimates["Medical Gas Piping"] = "Complete MGPS system"
                        material_estimates["HEPA Filters"] = f"{num_floors * 4} units"
                        material_estimates["Anti-bacterial Laminates"] = f"{total_area * 0.2:,.0f} sqft"
                        material_estimates["Lead Lining (X-ray rooms)"] = f"{total_area * 0.05:,.0f} sqft"
                    
                    cols = st.columns(3)
                    items = list(material_estimates.items())
                    for i, (key, value) in enumerate(items[:6]):  # Show first 6
                        cols[i % 3].metric(key, str(value))
                    
                    with st.expander("View all materials"):
                        for key, value in material_estimates.items():
                            st.write(f"**{key}:** {value}")
                else:
                    st.warning("Total area not detected. Cannot estimate materials.")
                
                # -------- Cost Estimation --------
                st.subheader("💰 Estimated Cost")
                if total_area > 0:
                    cost_estimates = estimate_costs(total_area * complexity)
                    cost_cols = st.columns(2)
                    cost_cols[0].write(f"**Base Construction Cost:** ₹{cost_estimates['Base Cost']:,.2f}")
                    cost_cols[0].write(f"**GST (18%):** ₹{cost_estimates['GST (18%)']:,.2f}")
                    cost_cols[1].write(f"**Contingency (5%):** ₹{cost_estimates['Contingency (5%)']:,.2f}")
                    cost_cols[1].success(f"**Total Estimated Cost:** ₹{cost_estimates['Total Estimated Cost']:,.2f}")
                    
                    # Special costs for hospitals
                    if building_type == "Hospital":
                        st.info("**Additional Hospital-Specific Costs:**")
                        add_cols = st.columns(3)
                        add_cols[0].metric("Medical Equipment", "₹5,00,00,000")
                        add_cols[1].metric("Medical Gas System", "₹2,50,00,000")
                        add_cols[2].metric("HVAC (Clean Rooms)", "₹3,00,00,000")
                else:
                    st.warning("Cannot estimate cost without area.")
                
                # -------- Duration Estimation --------
                st.subheader("📅 Project Duration")
                if total_area > 0:
                    # Base duration formula
                    base_duration = estimate_duration(total_area, num_floors)
                    
                    # Adjust for complexity
                    adjusted_duration = base_duration * complexity
                    
                    # Hospital-specific adjustments
                    if building_type == "Hospital":
                        # Hospitals take longer due to specialized systems
                        adjusted_duration = max(adjusted_duration, 24)  # Minimum 24 months for hospital
                    
                    st.info(f"Estimated construction duration: **{adjusted_duration:.1f} months**")
                    
                    # Breakdown by phase
                    st.write("**Phase-wise Breakdown:**")
                    phase_cols = st.columns(3)
                    phase_cols[0].write(f"**Foundation:** {adjusted_duration * 0.12:.1f} months")
                    phase_cols[0].write(f"**Structure:** {adjusted_duration * 0.25:.1f} months")
                    phase_cols[1].write(f"**MEP Work:** {adjusted_duration * 0.25:.1f} months")
                    phase_cols[1].write(f"**Finishing:** {adjusted_duration * 0.20:.1f} months")
                    phase_cols[2].write(f"**Commissioning:** {adjusted_duration * 0.18:.1f} months")
                else:
                    st.warning("Cannot estimate duration without area.")
                
                # -------- Team Allocation --------
                st.subheader("👷 Team Allocation")
                if total_area > 0:
                    # Calculate required staff based on area and complexity
                    if building_type == "Hospital":
                        required_engineers = max(8, int(total_area / 5000))
                        required_workers = max(50, int(total_area / 500))
                        required_managers = 3
                    else:
                        required_engineers = max(3, int(total_area / 10000))
                        required_workers = max(15, int(total_area / 1000))
                        required_managers = 1
                    
                    st.write(f"**Recommended Team Size:**")
                    st.write(f"- Engineers: {required_engineers}")
                    st.write(f"- Workers: {required_workers}")
                    st.write(f"- Project Managers: {required_managers}")
                    
                    # Assign available staff if project is selected
                    if project_choice != "None":
                        project_df = get_projects()[get_projects()["Project Name"] == project_choice]
                        if not project_df.empty:
                            project_id = project_df.iloc[0]["Project ID"]
                            project_location = project_df.iloc[0]["Location"]
                            assigned_manager = get_project_manager(project_id)
                            st.write(f"**Linked Project:** {project_choice}")
                            st.write(f"**Location:** {project_location}")
                            st.write(f"**Assigned Project Manager:** {assigned_manager}")
                            
                            # Select available staff
                            available_eng, available_wrk = select_available_staff(required_engineers, required_workers)
                            st.write("**Available Staff Assignment**")
                            st.write(f"Engineers: {', '.join(available_eng['Name'].tolist()) if not available_eng.empty else 'None available'}")
                            st.write(f"Workers: {', '.join(available_wrk['Name'].tolist()) if not available_wrk.empty else 'None available'}")
                        else:
                            st.info("Selected project not found.")
                    else:
                        # Show generic recommendations
                        st.write("**Recommended Team Structure:**")
                        st.write(f"- Lead Architect: 1")
                        st.write(f"- Structural Engineer: {max(1, int(required_engineers * 0.3))}")
                        st.write(f"- MEP Engineer: {max(1, int(required_engineers * 0.2))}")
                        st.write(f"- Site Supervisors: {max(2, int(required_workers * 0.05))}")
                        st.write(f"- Skilled Workers: {int(required_workers * 0.5)}")
                        st.write(f"- General Workers: {int(required_workers * 0.5)}")
                else:
                    st.warning("Cannot estimate team size without area.")
                
                # -------- AI Full Analysis Report --------
                st.subheader("🔎 AI Building Analysis Report")
                if st.button("Generate AI Analysis Report"):
                    with st.spinner("Generating comprehensive report..."):
                        prompt = f"""
    You are an expert construction analyst. Given the following extracted data from a building plan, provide a comprehensive construction analysis report.

    **Detected Building Type:** {building_type}
    **Total Area:** {total_area} sqft
    **Number of Floors:** {num_floors}
    **Capacity:** {capacity} (if applicable)

    **Extracted Text from Document:**
    {user_text[:2000]}

    **Estimated Material Quantities:**
    {estimate_materials(total_area * complexity) if total_area > 0 else "Area not detected"}

    **Estimated Cost Breakdown:**
    {estimate_costs(total_area * complexity) if total_area > 0 else "Area not detected"}

    **Estimated Duration:** {adjusted_duration:.1f} months if total_area > 0 else "N/A"

    **Your Task:**
    1. **Classify the Building Type**: Based on the document content, confirm the building type and provide justification.
    2. **Project Scope Summary**: Describe the key features, scale, and requirements of this project.
    3. **Material & Cost Analysis**: Explain the estimated material quantities and cost breakdown in simple terms.
    4. **Construction Timeline**: Provide a realistic timeline with major milestones.
    5. **Team Recommendation**: Suggest the required team structure (engineers, workers, managers).
    6. **Critical Considerations**: Highlight any special requirements (medical gas, clean rooms, lead lining, etc.).
    7. **Recommendations**: Suggest any design improvements or missing information needed for accurate estimation.

    Be professional, use bullet points, and keep the report concise yet thorough.
    """
                        analysis = ask_llm(prompt)
                    st.success("✅ Analysis complete")
                    st.markdown(analysis)
                else:
                    st.info("Click the button above to generate a comprehensive AI analysis report.")
        else:
            st.info("Please upload a blueprint or enter building details manually to start analysis.")
        # Tab 2: Risk Analysis
    with tabs[2]:
        st.subheader("Risk Detection")
        if st.button("Analyze Risks for All Projects"):
            projects = get_projects()
            budget_util = st.session_state.budget_util
            materials = st.session_state.materials
            equipment = st.session_state.equipment
            workers = get_workers()
            purchase_orders = st.session_state.purchase_orders
            safety = st.session_state.safety_quality
            data_summary = f"""
            Total projects: {len(projects)}
            Projects by status: {projects['Status'].value_counts().to_dict()}
            Budget utilization: {budget_util[['Project Name', 'Spent', 'Allocated']].head(3).to_dict()}
            Material stock: {materials[['Material Name', 'Available Quantity']].head(3).to_dict()}
            Equipment availability: {equipment['Availability'].value_counts().to_dict()}
            Workers: {len(workers)}
            Purchase orders status: {purchase_orders['Status'].value_counts().to_dict() if not purchase_orders.empty else 'N/A'}
            Safety data: {safety[['Project Name', 'Safety Score']].head(3).to_dict()}
            """
            prompt = f"""
            Analyze the following construction project data and identify risks across these categories:
            - Budget risk
            - Schedule risk
            - Material risk
            - Supplier risk
            - Equipment risk
            - Labour risk
            - Quality risk
            - Safety risk
            For each risk, provide: Severity (Low/Medium/High), Cause, Impact, Recommendation, Priority.
            Data:
            {data_summary}
            """
            with st.spinner("Analyzing risks..."):
                response = ask_llm(prompt)
            st.markdown(response)

    # Tab 3: Safety Assistant
    with tabs[3]:
        st.subheader("Site Safety Monitoring")
        uploaded_image = st.file_uploader("Upload site image for safety analysis", type=["jpg", "png", "jpeg"])
        if uploaded_image:
            st.image(uploaded_image, caption="Uploaded Image", width=300)
            st.info("AI will analyze this image for PPE compliance (helmet, vest, gloves, safety shoes) and identify unsafe behaviour. This feature will be available with computer vision integration in future milestones.")
        st.subheader("Safety Evaluation")
        ppe_compliance = st.slider("PPE Compliance (%)", 0, 100, 80)
        incidents = st.number_input("Incidents this month", min_value=0, value=0)
        weather = st.text_input("Current weather", "Clear")
        hazards = st.text_area("Reported hazards", "None")
        if st.button("Evaluate Safety"):
            prompt = f"""
            Evaluate site safety:
            - PPE: {ppe_compliance}%
            - Incidents: {incidents}
            - Weather: {weather}
            - Hazards: {hazards}
            Provide safety score, potential hazards, recommendations, emergency precautions, compliance suggestions.
            """
            with st.spinner("Analyzing safety..."):
                response = ask_llm(prompt)
            st.markdown(response)

def reports_page():
    import io
    import textwrap
    from datetime import datetime
    import streamlit as st
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    st.title("📄 Reports")
    report_tabs = st.tabs(["Daily Report"])

    with report_tabs[0]:
        st.subheader("Generate Daily Report")

        project_list = ["Select a project"] + get_projects()["Project Name"].tolist()
        selected_project = st.selectbox("Choose Project", project_list)

        if selected_project != "Select a project":

            project = get_projects()[get_projects()["Project Name"] == selected_project].iloc[0]

            project_id = project["Project ID"]
            project_location = project["Location"]
            project_manager = get_project_manager(project_id)
            report_date = datetime.today().strftime("%Y-%m-%d")

            

            st.markdown(
                f"**Project:** {selected_project} &nbsp;&nbsp;&nbsp; "
                f"**Project ID:** {project_id}"
            )

            weather = st.text_input("Weather conditions", "Sunny, 30°C")
            labor_count = st.number_input("Workers present", min_value=0, value=20)
            materials_used = st.text_area(
                "Materials used today",
                "Cement 50 bags, Steel 2 tons"
            )
            equipment_status = st.text_input(
                "Equipment status",
                "All working"
            )
            site_issues = st.text_area(
                "Site issues (if any)",
                "None"
            )

            # Generate Report
            if st.button("Generate Daily Report"):

                prompt = f"""
Generate a professional daily construction report.

Project Name: {selected_project}
Project ID: {project_id}
Date: {report_date}
Location: {project_location}
Project Manager: {project_manager}
Weather: {weather}
Workers Present: {labor_count}
Materials Used: {materials_used}
Equipment Status: {equipment_status}
Site Issues: {site_issues}

Include:
1. Executive Summary
2. Work Completed
3. Progress
4. Delays
5. Risks
6. Recommendations
7. Next Day Plan
"""

                with st.spinner("Generating Report..."):
                    st.session_state.daily_report = ask_llm(prompt)

            # Display report if available
            if "daily_report" in st.session_state:

                report = st.session_state.daily_report

                st.markdown("## 📄 Daily Report")
                st.markdown(report)

                st.markdown("---")
                st.markdown("**Site Engineer Signature:** ________________________")

                # ---------------- PDF Creation ----------------
                pdf_buffer = io.BytesIO()

                c = canvas.Canvas(pdf_buffer, pagesize=letter)
                width, height = letter

                y = height - 50

                c.setFont("Helvetica-Bold", 16)
                c.drawString(50, y, "Construction Daily Report")

                y -= 30
                c.setFont("Helvetica", 11)

                c.drawString(50, y, f"Project : {selected_project}")
                y -= 18

                c.drawString(50, y, f"Project ID : {project_id}")
                y -= 18

                c.drawString(50, y, f"Date : {report_date}")
                y -= 18

                c.drawString(50, y, f"Location : {project_location}")
                y -= 18

                c.drawString(50, y, f"Project Manager : {project_manager}")
                y -= 30

                clean_report = (
                    report.replace("**", "")
                          .replace("##", "")
                          .replace("*", "")
                )

                c.setFont("Helvetica", 11)

                for paragraph in clean_report.split("\n"):

                    wrapped_lines = textwrap.wrap(paragraph, width=90)

                    if not wrapped_lines:
                        y -= 15
                        continue

                    for line in wrapped_lines:

                        if y < 60:
                            c.showPage()
                            c.setFont("Helvetica", 11)
                            y = height - 50

                        c.drawString(50, y, line)
                        y -= 15

                y -= 25

                if y < 60:
                    c.showPage()
                    c.setFont("Helvetica", 11)
                    y = height - 50

                c.drawString(50, y, "Site Engineer Signature: ________________________")

                c.save()
                pdf_buffer.seek(0)

                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_buffer.getvalue(),
                    file_name=f"{selected_project}_Daily_Report_{report_date}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
# ===================== Safety & Quality (unchanged) =====================
def safety_quality_page():
    st.title("🛡️ Safety & Quality")
    sq = st.session_state.safety_quality
    st.dataframe(sq, use_container_width=True)
    fig = px.histogram(sq, x="Safety Score", nbins=20, title="Safety Score Distribution")
    st.plotly_chart(fig, use_container_width=True)
    quality_cols = ["Concrete Quality", "Brickwork Quality", "Plaster Quality", "Finishing Quality"]
    quality_counts = pd.DataFrame()
    for col in quality_cols:
        counts = sq[col].value_counts().reset_index()
        counts.columns = ["Quality", "Count"]
        counts["Aspect"] = col
        quality_counts = pd.concat([quality_counts, counts])
    fig = px.bar(quality_counts, x="Aspect", y="Count", color="Quality", barmode="group", title="Quality Ratings")
    st.plotly_chart(fig, use_container_width=True)

# ------------------- Navigation -------------------
def main_app():
    with st.sidebar:
        st.title("🏗️ Construction Hub")
        st.write(f"**Role:** {st.session_state.role}")
        if st.button("Logout"):
            logout()
        st.divider()
        dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
        if dark_mode != st.session_state.dark_mode:
            st.session_state.dark_mode = dark_mode
            st.rerun()
        st.divider()
        menu_items = ["Dashboard", "Projects", "Resources", "Workforce", "AI Assistant", "Safety & Quality", "Reports", "About"]
        if st.session_state.role == "Client":
            menu_items = ["Dashboard", "My Project", "About"]
        elif st.session_state.role == "Project Manager":
            menu_items = ["Dashboard", "Projects", "Resources", "Workforce", "AI Assistant", "Reports", "About"]
        elif st.session_state.role == "Site Engineer":
            menu_items = ["Dashboard", "Projects", "Resources", "Workforce", "AI Assistant", "Safety & Quality", "Reports", "About"]
        choice = st.radio("Navigate", menu_items, index=0)
        st.session_state.page = choice

    page = st.session_state.page
    if page == "Dashboard":
        dashboard_page()
    elif page == "Projects":
        project_management_page()
    elif page == "My Project":
        client_portal_page()
    elif page == "Resources":
        resource_management_page()
    elif page == "Workforce":
        workforce_page()
    elif page == "AI Assistant":
        ai_assistant_page()
    elif page == "Safety & Quality":
        safety_quality_page()
    elif page == "Reports":
        reports_page()
    elif page == "About":
        about_page()
    else:
        st.write("Page under construction")

# ------------------- Main Execution -------------------
if not st.session_state.logged_in:
    login()
else:
    main_app()