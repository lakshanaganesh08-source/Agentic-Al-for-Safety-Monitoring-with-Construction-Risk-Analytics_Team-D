import streamlit as st

AMBER = "#F59E0B"
STEEL = "#3B82F6"
GREEN = "#22C55E"
RED = "#F87171"
BG = "#0B1220"
BG2 = "#111A2E"
TEXT = "#E5E7EB"
MUTED = "#8CA0BF"


def inject_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        .cih-hero {{
            background: linear-gradient(135deg, {BG2} 0%, {BG} 100%);
            border: 1px solid #1E2E4A;
            border-radius: 14px;
            padding: 22px 26px;
            margin-bottom: 18px;
        }}
        .cih-hero-badge {{
            display: inline-block;
            background: {AMBER}22;
            color: {AMBER};
            border: 1px solid {AMBER}55;
            border-radius: 999px;
            padding: 3px 12px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            margin-bottom: 10px;
        }}
        .cih-hero-title {{
            font-family: 'Barlow Condensed', sans-serif;
            font-size: 2.1rem;
            font-weight: 800;
            color: {TEXT};
            margin: 0 0 6px 0;
        }}
        .cih-hero-sub {{
            color: {MUTED};
            font-size: 0.95rem;
            line-height: 1.5;
            max-width: 900px;
        }}

        .cih-section-label {{
            font-family: 'Barlow Condensed', sans-serif;
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            color: {MUTED};
            border-left: 3px solid {AMBER};
            padding-left: 10px;
            margin: 18px 0 10px 0;
            text-transform: uppercase;
        }}

        .cih-card {{
            background: {BG2};
            border: 1px solid #1E2E4A;
            border-radius: 12px;
            padding: 14px 16px;
        }}

        .cih-kpi {{
            background: {BG2};
            border: 1px solid #1E2E4A;
            border-radius: 12px;
            padding: 14px 16px;
            height: 100%;
        }}
        .cih-kpi-icon {{ font-size: 1.3rem; }}
        .cih-kpi-label {{
            color: {MUTED};
            font-size: 0.78rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-top: 6px;
        }}
        .cih-kpi-value {{
            font-family: 'Barlow Condensed', sans-serif;
            font-size: 1.7rem;
            font-weight: 800;
            color: {TEXT};
            margin-top: 2px;
        }}
        .cih-kpi-delta-up {{ color: {GREEN}; font-size: 0.78rem; font-weight: 600; }}
        .cih-kpi-delta-down {{ color: {RED}; font-size: 0.78rem; font-weight: 600; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, badge: str | None = None):
    badge_html = f'<div class="cih-hero-badge">{badge}</div>' if badge else ""
    st.markdown(
        f"""<div class="cih-hero">
        {badge_html}
        <div class="cih-hero-title">{title}</div>
        <div class="cih-hero-sub">{subtitle}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def section_label(text: str):
    st.markdown(f'<div class="cih-section-label">{text}</div>', unsafe_allow_html=True)


def kpi_card(icon: str, label: str, value: str, delta_text: str, positive: bool = True):
    delta_class = "cih-kpi-delta-up" if positive else "cih-kpi-delta-down"
    arrow = "▲" if positive else "▼"
    st.markdown(
        f"""<div class="cih-kpi">
        <div class="cih-kpi-icon">{icon}</div>
        <div class="cih-kpi-label">{label}</div>
        <div class="cih-kpi-value">{value}</div>
        <div class="{delta_class}">{arrow} {delta_text}</div>
        </div>""",
        unsafe_allow_html=True,
    )
