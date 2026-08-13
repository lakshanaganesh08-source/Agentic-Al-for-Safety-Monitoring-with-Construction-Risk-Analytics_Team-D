import streamlit as st
import plotly.graph_objects as go
from utils.data_gen import get_sample_applications_data


def _inject_css():
    st.markdown("""
        <style>
        @keyframes pulse-dot {
            0%   { box-shadow: 0 0 0 0 rgba(0, 230, 118, 0.55); }
            70%  { box-shadow: 0 0 0 10px rgba(0, 230, 118, 0); }
            100% { box-shadow: 0 0 0 0 rgba(0, 230, 118, 0); }
        }
        @keyframes glow-pulse {
            0%, 100% { box-shadow: 0 0 14px 2px rgba(255, 171, 0, 0.55); }
            50%      { box-shadow: 0 0 22px 6px rgba(255, 171, 0, 0.85); }
        }
        @keyframes fill-bar {
            from { width: 0%; }
        }

        .ci-hero {
            text-align: center;
            padding: 6px 0 4px 0;
        }
        .ci-hero-badge {
            width: 64px; height: 64px;
            margin: 0 auto 14px auto;
            border-radius: 18px;
            display: flex; align-items: center; justify-content: center;
            font-size: 2rem;
            background: linear-gradient(135deg, rgba(0,229,255,0.18), rgba(124,58,237,0.18));
            border: 1px solid rgba(0,229,255,0.35);
            box-shadow: 0 0 30px rgba(0,229,255,0.25);
        }
        .ci-hero h1 {
            font-size: 2.3rem !important;
            background: linear-gradient(90deg, #00E5FF, #7C3AED 60%, #FF2E93);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 6px !important;
        }
        .ci-hero p {
            color: #8B949E; font-size: 1.05rem; font-weight: 500;
        }
        .ci-active-pill {
            display: inline-flex; align-items: center; gap: 8px;
            background: rgba(0, 230, 118, 0.10);
            border: 1px solid #00E676;
            color: #00E676;
            border-radius: 999px;
            padding: 6px 18px;
            font-size: 0.82rem; font-weight: 700;
            margin-top: 14px;
        }
        .ci-active-pill .dot {
            width: 8px; height: 8px; border-radius: 50%;
            background: #00E676;
            animation: pulse-dot 1.8s infinite;
        }

        .ci-section-title {
            display: flex; align-items: center; gap: 10px;
            color: #F0F6FC; font-size: 1.15rem; font-weight: 800;
            margin: 6px 0 16px 0;
        }
        .ci-section-title .bar {
            width: 4px; height: 20px; border-radius: 3px;
            background: linear-gradient(180deg, #00E5FF, #7C3AED);
        }

        .ci-feature-card {
            background: linear-gradient(145deg, #161B22 0%, #12161D 100%);
            border: 1px solid #262C36;
            border-radius: 14px;
            padding: 16px 16px;
            margin-bottom: 14px;
            display: flex; align-items: center; gap: 12px;
            transition: transform 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease;
        }
        .ci-feature-card:hover {
            transform: translateY(-4px);
            border-color: rgba(0, 229, 255, 0.45);
            box-shadow: 0 10px 26px rgba(0, 229, 255, 0.12);
        }
        .ci-feature-icon {
            flex-shrink: 0;
            width: 40px; height: 40px;
            border-radius: 11px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.15rem;
        }
        .ci-feature-label {
            color: #E6EDF3; font-size: 0.9rem; font-weight: 650;
            line-height: 1.25;
        }

        .ci-kpi-card {
            border-radius: 16px;
            padding: 18px 20px;
            margin-bottom: 14px;
            position: relative;
            overflow: hidden;
            transition: transform 0.22s ease;
        }
        .ci-kpi-card:hover { transform: translateY(-3px); }
        .ci-kpi-label {
            font-size: 0.76rem; font-weight: 800; letter-spacing: 0.6px;
            text-transform: uppercase; display: flex; align-items: center; gap: 6px;
        }
        .ci-kpi-value {
            font-size: 2rem; font-weight: 850; margin-top: 8px;
        }

        .ci-metric-tile {
            background: linear-gradient(145deg, #161B22, #10141B);
            border: 1px solid #262C36;
            border-radius: 14px;
            padding: 20px;
            text-align: center;
        }
        .ci-metric-tile .lbl { color: #8B949E; font-size: 0.82rem; font-weight: 700; letter-spacing: 0.5px; }
        .ci-metric-tile .val { font-size: 2.1rem; font-weight: 850; margin-top: 6px; }

        .ci-timeline-wrap {
            display: flex; align-items: flex-start; justify-content: space-between;
            position: relative;
            padding: 10px 6px 0 6px;
        }
        .ci-timeline-wrap::before {
            content: "";
            position: absolute;
            top: 30px; left: 6%; right: 6%;
            height: 3px;
            background: linear-gradient(90deg, #00E676 0%, #00E676 33%, #FFAB00 33%, #FFAB00 66%, #30363D 66%, #30363D 100%);
            border-radius: 3px;
            z-index: 0;
        }
        .ci-node {
            position: relative; z-index: 1;
            display: flex; flex-direction: column; align-items: center;
            width: 24%;
        }
        .ci-node-circle {
            width: 42px; height: 42px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.15rem; font-weight: 800;
            background: #0D111A;
            border: 3px solid #30363D;
        }
        .ci-node-circle.done { border-color: #00E676; background: rgba(0,230,118,0.12); color: #00E676; }
        .ci-node-circle.current { border-color: #FFAB00; background: rgba(255,171,0,0.14); color: #FFAB00; animation: glow-pulse 1.8s infinite; }
        .ci-node-circle.pending { border-color: #30363D; background: #0D111A; color: #4B5563; }
        .ci-node-label {
            margin-top: 10px; text-align: center; font-size: 0.78rem; font-weight: 650;
            color: #C9D1D9; max-width: 130px;
        }

        .ci-cat-row { margin-bottom: 18px; }
        .ci-cat-top { display: flex; justify-content: space-between; margin-bottom: 8px; align-items: center;}
        .ci-cat-name { color: #E6EDF3; font-size: 0.92rem; font-weight: 650; display:flex; align-items:center; gap:8px;}
        .ci-cat-pct { font-size: 0.92rem; font-weight: 800; }
        .ci-track { background: #1B212B; border-radius: 999px; height: 10px; width: 100%; overflow: hidden; }
        .ci-fill { height: 10px; border-radius: 999px; animation: fill-bar 1s ease-out; }
        </style>
    """, unsafe_allow_html=True)


def render():
    _inject_css()

    # ---------------------------------------------------------------
    # Hero header
    # ---------------------------------------------------------------
    st.markdown("""
        <div class="ci-hero">
            <div class="ci-hero-badge">🛡️</div>
            <h1>Compliance & Insurance Intelligence Dashboard</h1>
            <p>Regulatory Compliance, Audit Readiness & Insurance Risk in One View</p>
            <div class="ci-active-pill"><span class="dot"></span> Compliance Active</div>
        </div>
        <hr style="border: 0; height: 1px; background: linear-gradient(to right, rgba(0, 229, 255, 0), rgba(0, 229, 255, 0.75), rgba(0, 229, 255, 0)); margin: 30px 0;">
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------------
    # Feature list + KPI cards
    # ---------------------------------------------------------------
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown('<div class="ci-section-title"><span class="bar"></span> 📋 Compliance & Insurance Features</div>', unsafe_allow_html=True)

        features = [
            ("📊", "Regulatory Compliance Dashboard", "#00E5FF"),
            ("🔍", "Compliance Audit Results", "#7C3AED"),
            ("📈", "Claim Risk Analysis", "#FF2E93"),
            ("📁", "Documentation Status", "#FFAB00"),
            ("🕵️", "Inspection Tracking", "#00E676"),
            ("🏦", "Insurance Risk Assessment", "#00E5FF"),
            ("🚨", "Compliance Violation Monitoring", "#FF5252"),
            ("🎯", "Regulatory Readiness Score", "#7C3AED"),
        ]

        f_col1, f_col2 = st.columns(2, gap="medium")
        for i, (icon, label, color) in enumerate(features):
            target_col = f_col1 if i % 2 == 0 else f_col2
            with target_col:
                st.markdown(f"""
                    <div class="ci-feature-card">
                        <div class="ci-feature-icon" style="background: {color}22; border: 1px solid {color}55;">
                            {icon}
                        </div>
                        <div class="ci-feature-label">{label}</div>
                    </div>
                """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="ci-section-title"><span class="bar"></span> 📌 Key Performance Indicators</div>', unsafe_allow_html=True)

        k1, k2 = st.columns(2, gap="medium")
        with k1:
            st.markdown("""
                <div class="ci-kpi-card" style="background: linear-gradient(145deg, rgba(0,230,118,0.14), rgba(0,230,118,0.04)); border: 1px solid #00E676;">
                    <div class="ci-kpi-label" style="color:#00E676;">✅ Compliance Score</div>
                    <div class="ci-kpi-value" style="color:#00E676;">96.4%</div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("""
                <div class="ci-kpi-card" style="background: linear-gradient(145deg, rgba(255,171,0,0.14), rgba(255,171,0,0.04)); border: 1px solid #FFAB00;">
                    <div class="ci-kpi-label" style="color:#FFAB00;">🏦 Insurance Risk Score</div>
                    <div class="ci-kpi-value" style="color:#FFAB00; font-size:1.6rem;">Medium</div>
                </div>
            """, unsafe_allow_html=True)

        with k2:
            st.markdown("""
                <div class="ci-kpi-card" style="background: linear-gradient(145deg, rgba(255,82,82,0.14), rgba(255,82,82,0.04)); border: 1px solid #FF5252;">
                    <div class="ci-kpi-label" style="color:#FF5252;">⚠️ Open Violations</div>
                    <div class="ci-kpi-value" style="color:#FF5252;">5</div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("""
                <div class="ci-kpi-card" style="background: linear-gradient(145deg, rgba(0,229,255,0.14), rgba(0,229,255,0.04)); border: 1px solid #00E5FF;">
                    <div class="ci-kpi-label" style="color:#00E5FF;">📁 Audit Readiness</div>
                    <div class="ci-kpi-value" style="color:#00E5FF;">92%</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr style='border: 0; height: 1px; background: #30363D; margin: 34px 0;'>", unsafe_allow_html=True)

    # ---------------------------------------------------------------
    # Applications section
    # ---------------------------------------------------------------
    st.markdown('<div class="ci-section-title"><span class="bar"></span> 📥 Applications</div>', unsafe_allow_html=True)

    a_col1, a_col2 = st.columns(2, gap="medium")
    with a_col1:
        st.markdown("""
            <div class="ci-metric-tile">
                <div class="lbl">APP APPROVAL RATE</div>
                <div class="val" style="color:#00E676;">86.36%</div>
            </div>
        """, unsafe_allow_html=True)
    with a_col2:
        st.markdown("""
            <div class="ci-metric-tile">
                <div class="lbl">APP PROCESSING TIME</div>
                <div class="val" style="color:#00E5FF;">8 days</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8B949E; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.5px;'>APPLICATIONS CREATED + SUBMITTED</p>", unsafe_allow_html=True)

    df_apps = get_sample_applications_data()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_apps["Month"], y=df_apps["Created"], name="Created",
        marker=dict(color="#2A303C", line=dict(width=0)),
        width=0.34,
    ))
    fig.add_trace(go.Bar(
        x=df_apps["Month"], y=df_apps["Submitted"], name="Submitted",
        marker=dict(
            color=df_apps["Submitted"],
            colorscale=[[0, "#0088FF"], [1, "#00E5FF"]],
            line=dict(width=0),
        ),
        width=0.34,
    ))
    for trace in fig.data:
        trace.update(marker_cornerradius=6)

    fig.update_layout(
        barmode="group",
        bargap=0.28,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8B949E", family="Plus Jakarta Sans, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1, title=None,
                    font=dict(color="#C9D1D9")),
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#1B212B", zeroline=False),
        hoverlabel=dict(bgcolor="#161B22", font_color="#F0F6FC", bordercolor="#00E5FF"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Checkpoints — timeline style
    st.markdown("<p style='color: #8B949E; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.5px; margin-top: 10px;'>CHECKPOINTS</p>", unsafe_allow_html=True)

    checkpoints = [
        ("✓", "Permit Application Submitted", "done"),
        ("✓", "Initial Regulatory Review", "done"),
        ("●", "Insurance Underwriting Review", "current"),
        ("", "Final Compliance Sign-off", "pending"),
    ]
    node_parts = []
    for icon, label, state in checkpoints:
        node_parts.append(
            f'<div class="ci-node"><div class="ci-node-circle {state}">{icon}</div>'
            f'<div class="ci-node-label">{label}</div></div>'
        )
    nodes_html = '<div class="ci-timeline-wrap">' + "".join(node_parts) + "</div>"
    st.markdown(nodes_html, unsafe_allow_html=True)

    st.markdown("<hr style='border: 0; height: 1px; background: #30363D; margin: 40px 0 30px 0;'>", unsafe_allow_html=True)

    # ---------------------------------------------------------------
    # Compliance Status by Category
    # ---------------------------------------------------------------
    st.markdown('<div class="ci-section-title"><span class="bar"></span> 📊 Compliance Status by Category</div>', unsafe_allow_html=True)

    categories = [
        ("🦺", "OSHA Standards", 98, "#00E676"),
        ("🏗️", "Building Codes", 95, "#00E5FF"),
        ("🌱", "Environmental Regulations", 94, "#FFAB00"),
        ("🏦", "Insurance Requirements", 91, "#7C3AED"),
    ]

    for icon, name, pct, color in categories:
        st.markdown(f"""
            <div class="ci-cat-row">
                <div class="ci-cat-top">
                    <span class="ci-cat-name">{icon} {name}</span>
                    <span class="ci-cat-pct" style="color:{color};">{pct}%</span>
                </div>
                <div class="ci-track">
                    <div class="ci-fill" style="width:{pct}%; background: linear-gradient(90deg, {color}AA, {color});"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
