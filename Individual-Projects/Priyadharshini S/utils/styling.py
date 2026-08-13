import streamlit as st


def apply_custom_css():
    st.markdown(
        """
        <style>
        /* Import Modern Typography */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        :root {
            color-scheme: dark;
            --accent-cyan: #00E5FF;
            --accent-blue: #0088FF;
            --accent-purple: #7C3AED;
            --accent-pink: #FF2E93;
            --accent-green: #00E676;
            --accent-amber: #FFAB00;
            --accent-red: #FF5252;
            --surface: #161B22;
            --surface-2: #0D1117;
            --border: #30363D;
            --text-dim: #8B949E;
            --text-bright: #F0F6FC;
        }

        /* Base App Canvas & Modern Background */
        .stApp {
            background:
                radial-gradient(circle at 15% 15%, rgba(0, 229, 255, 0.12), transparent 30%),
                radial-gradient(circle at 85% 85%, rgba(124, 58, 237, 0.12), transparent 30%),
                linear-gradient(180deg, #090D16 0%, #0D111A 100%);
            color: #E2E8F0;
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Glassmorphic Sidebar Styling */
        [data-testid="stSidebar"] {
            background: rgba(13, 17, 23, 0.85) !important;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        }

        /* Typography & Headings Styling */
        h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #F8FAFC !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
        }

        /* Modern High-Glow Gradient Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #00E5FF 0%, #0088FF 50%, #7C3AED 100%) !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
            border-radius: 12px !important;
            padding: 0.75rem 1.5rem !important;
            border: none !important;
            box-shadow: 0 4px 20px rgba(0, 229, 255, 0.25) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        .stButton > button:hover {
            opacity: 0.95 !important;
            transform: translateY(-2px) scale(1.01) !important;
            box-shadow: 0 8px 30px rgba(0, 229, 255, 0.45) !important;
        }

        .stButton > button:active {
            transform: translateY(0px) scale(0.99) !important;
        }

        /* Form Controls: Text Inputs, Text Areas, Select Boxes */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > div,
        .stNumberInput > div > div > input {
            background: #161B22 !important;
            color: #F0F6FC !important;
            border: 1px solid #30363D !important;
            border-radius: 10px !important;
            padding: 0.65rem 0.85rem !important;
            transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
        }

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #00E5FF !important;
            box-shadow: 0 0 0 3px rgba(0, 229, 255, 0.2) !important;
        }

        /* Alert Banners Styling */
        .stAlert {
            border-radius: 14px !important;
            backdrop-filter: blur(8px) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }

        /* Custom Modern Scrollbars */
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: #0D111A; }
        ::-webkit-scrollbar-thumb { background: #21262D; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #30363D; }

        /* ===================== SHARED DESIGN SYSTEM ===================== */

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(14px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes floatGlow {
            0%   { transform: translate(0px, 0px) scale(1); }
            50%  { transform: translate(16px, -20px) scale(1.06); }
            100% { transform: translate(0px, 0px) scale(1); }
        }
        @keyframes pulseDot {
            0%   { box-shadow: 0 0 0 0 rgba(0,230,118,0.55); }
            70%  { box-shadow: 0 0 0 8px rgba(0,230,118,0); }
            100% { box-shadow: 0 0 0 0 rgba(0,230,118,0); }
        }

        .hub-fade-in { animation: fadeInUp 0.55s ease-out; }

        /* Page hero header */
        .hub-hero {
            text-align: center;
            padding: 14px 0 22px 0;
            position: relative;
            animation: fadeInUp 0.6s ease-out;
        }
        .hub-hero .hub-badge {
            display: inline-flex; align-items: center; gap: 8px;
            background: rgba(0, 229, 255, 0.1); border: 1px solid rgba(0, 229, 255, 0.35);
            border-radius: 999px; padding: 5px 14px; font-size: 0.72rem; font-weight: 700;
            color: #00E5FF; letter-spacing: 0.6px; margin-bottom: 14px;
        }
        .hub-hero h1 {
            font-size: 2.3rem !important; margin: 0 0 8px 0 !important;
            background: linear-gradient(135deg, #FFFFFF 25%, #00E5FF 70%, #7C3AED 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
        }
        .hub-hero p {
            color: #8B949E; font-size: 1.05rem; font-weight: 500; margin: 0 auto;
            max-width: 620px;
        }
        .hub-divider {
            border: 0; height: 1px;
            background: linear-gradient(to right, rgba(0,229,255,0), rgba(0,229,255,0.65), rgba(124,58,237,0.5), rgba(0,229,255,0));
            margin: 22px 0 28px 0;
        }

        /* Glass / feature cards with hover lift */
        .hub-card {
            background: linear-gradient(180deg, rgba(22,27,34,0.92), rgba(13,17,23,0.92));
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 20px;
            transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
            animation: fadeInUp 0.6s ease-out;
            height: 100%;
        }
        .hub-card:hover {
            transform: translateY(-4px);
            border-color: rgba(0,229,255,0.35);
            box-shadow: 0 14px 40px rgba(0,229,255,0.12);
        }
        .hub-card .hub-card-icon {
            width: 44px; height: 44px; border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.25rem; margin-bottom: 12px;
            background: linear-gradient(135deg, rgba(0,229,255,0.18), rgba(124,58,237,0.18));
            border: 1px solid rgba(255,255,255,0.08);
        }
        .hub-card h4 { margin: 0 0 6px 0 !important; font-size: 1.05rem !important; color: #F0F6FC !important; }
        .hub-card .hub-card-tag { color: #00E5FF; font-size: 0.8rem; font-weight: 600; }
        .hub-card p.hub-card-body { color: #C9D1D9; font-size: 0.9rem; margin: 6px 0 0 0; line-height: 1.5; }

        /* KPI / stat cards */
        .hub-stat {
            background: linear-gradient(180deg, rgba(22,27,34,0.92), rgba(13,17,23,0.92));
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 18px 16px;
            text-align: center;
            position: relative;
            overflow: hidden;
            transition: transform 0.25s ease, box-shadow 0.25s ease;
            animation: fadeInUp 0.6s ease-out;
        }
        .hub-stat:hover { transform: translateY(-3px); box-shadow: 0 12px 34px rgba(0,0,0,0.35); }
        .hub-stat .hub-stat-icon { font-size: 1.4rem; margin-bottom: 6px; display: block; }
        .hub-stat .hub-stat-label {
            color: #8B949E; margin: 0; font-size: 0.78rem; font-weight: 700;
            letter-spacing: 0.6px; text-transform: uppercase;
        }
        .hub-stat .hub-stat-value {
            font-size: 1.7rem; font-weight: 800; margin: 6px 0 2px 0;
        }
        .hub-stat .hub-stat-delta { font-size: 0.78rem; font-weight: 700; }

        /* Status / severity strip cards */
        .hub-strip {
            background-color: #161B22;
            border-left: 4px solid var(--accent-cyan);
            padding: 12px 16px;
            border-radius: 0 10px 10px 0;
            margin-bottom: 10px;
            animation: fadeInUp 0.5s ease-out;
        }
        .hub-strip b { font-weight: 700; }
        .hub-strip p { color: #C9D1D9; font-size: 0.88rem; margin: 3px 0 0 0; }

        /* Pill badge (e.g. connection status) */
        .hub-pill {
            border-radius: 999px; padding: 5px 14px; font-weight: 700; font-size: 0.78rem;
            display: inline-flex; align-items: center; gap: 6px;
        }
        .hub-pulse-dot {
            width: 8px; height: 8px; border-radius: 50%; background: #00E676;
            animation: pulseDot 1.8s infinite;
        }

        /* Sticky info banner */
        .hub-banner {
            background: linear-gradient(135deg, rgba(0,229,255,0.08), rgba(124,58,237,0.08));
            border: 1px solid rgba(0,229,255,0.25);
            border-radius: 14px;
            padding: 16px 18px;
            margin-bottom: 22px;
            animation: fadeInUp 0.6s ease-out;
        }

        /* Floating ambient orbs (used sparingly per page) */
        .hub-orb {
            position: fixed; border-radius: 50%; filter: blur(10px);
            z-index: 0; pointer-events: none; opacity: 0.6;
            animation: floatGlow 11s ease-in-out infinite;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_hero(icon: str, title: str, subtitle: str, badge: str = None):
    """
    Renders a shared gradient hero header used at the top of every page,
    with an optional small pill badge above the title.
    """
    badge_html = f'<span class="hub-badge">{badge}</span><br>' if badge else ""
    st.markdown(f"""
        <div class="hub-hero">
            {badge_html}
            <h1>{icon} {title}</h1>
            <p>{subtitle}</p>
        </div>
        <hr class="hub-divider">
    """, unsafe_allow_html=True)


def feature_card(icon: str, tag: str, title: str, body: str) -> str:
    """Returns HTML for a single hover-lift feature/info card. Wrap in st.markdown(..., unsafe_allow_html=True)."""
    return f"""
        <div class="hub-card">
            <div class="hub-card-icon">{icon}</div>
            <span class="hub-card-tag">{tag}</span>
            <h4>{title}</h4>
            <p class="hub-card-body">{body}</p>
        </div>
    """


def stat_card(icon: str, label: str, value: str, delta: str = None, color: str = "#00E5FF") -> str:
    """Returns HTML for a single KPI stat card."""
    delta_html = f'<div class="hub-stat-delta" style="color:{color};">{delta}</div>' if delta else ""
    return f"""
        <div class="hub-stat">
            <span class="hub-stat-icon">{icon}</span>
            <p class="hub-stat-label">{label}</p>
            <div class="hub-stat-value" style="color:{color};">{value}</div>
            {delta_html}
        </div>
    """


def status_strip(color: str, title: str, body: str) -> str:
    """Returns HTML for a colored left-border status/finding strip."""
    return f"""
        <div class="hub-strip" style="border-left-color:{color};">
            <span style="color:{color};">{title}</span>
            <p>{body}</p>
        </div>
    """


def section_header(icon: str, title: str, subtitle: str, tag: str = None):
    """Kept for backward compatibility — delegates to page_hero."""
    page_hero(icon, title, subtitle, badge=tag)
