import streamlit as st

from modules import site_risk_agent
from modules import safety_agent


def render():
    """
    Combined Safety & Risk Intelligence module.

    Combines:
    1. Site Risk Agent
    2. Safety Agent
    """

    # =========================================================
    # PAGE HEADER
    # =========================================================

    st.markdown(
        """
<div style="padding: 10px 0 25px 0;">

<h1 style="
    font-size: 2.5rem;
    margin-bottom: 5px;
    background: linear-gradient(90deg, #00D9FF, #7C4DFF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
">
🛡️ Safety & Risk Intelligence
</h1>

<p style="
    color: #8B949E;
    font-size: 1.05rem;
">
Unified construction site safety monitoring,
risk assessment and incident intelligence.
</p>

</div>
""",
        unsafe_allow_html=True
    )

    # =========================================================
    # OVERVIEW CARDS
    # =========================================================

    col1, col2, col3 = st.columns(3)

    # ---------------- SITE RISK CARD ----------------

    with col1:
        st.markdown(
            """
<div style="
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 12px;
    padding: 18px;
    text-align: center;
    min-height: 150px;
">

<div style="font-size: 2rem;">
⚠️
</div>

<h4 style="color: #FFFFFF; margin-bottom: 8px;">
Site Risk
</h4>

<p style="color: #C9D1D9; margin: 0;">
Identify and assess construction site risks.
</p>

</div>
""",
            unsafe_allow_html=True
        )

    # ---------------- SAFETY MANAGEMENT CARD ----------------

    with col2:
        st.markdown(
            """
<div style="
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 12px;
    padding: 18px;
    text-align: center;
    min-height: 150px;
">

<div style="font-size: 2rem;">
🦺
</div>

<h4 style="color: #FFFFFF; margin-bottom: 8px;">
Safety Management
</h4>

<p style="color: #C9D1D9; margin: 0;">
Monitor worker safety and compliance.
</p>

</div>
""",
            unsafe_allow_html=True
        )

    # ---------------- SAFETY INTELLIGENCE CARD ----------------

    with col3:
        st.markdown(
            """
<div style="
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 12px;
    padding: 18px;
    text-align: center;
    min-height: 150px;
">

<div style="font-size: 2rem;">
📊
</div>

<h4 style="color: #FFFFFF; margin-bottom: 8px;">
Safety Intelligence
</h4>

<p style="color: #C9D1D9; margin: 0;">
Combine risk and safety insights.
</p>

</div>
""",
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================================================
    # INTELLIGENCE CENTER
    # =========================================================

    st.markdown(
        """
<h2 style="
    color: #FFFFFF;
    margin-top: 10px;
    margin-bottom: 20px;
">
Intelligence Center
</h2>
""",
        unsafe_allow_html=True
    )

    selected_feature = st.radio(
        "Select an intelligence area:",
        [
            "⚠️ Site Risk Assessment",
            "🦺 Safety Management"
        ],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.markdown(
        """
<hr style="
    border: 0;
    height: 1px;
    background: #30363D;
    margin: 25px 0;
">
""",
        unsafe_allow_html=True
    )

    # =========================================================
    # SITE RISK ASSESSMENT
    # =========================================================

    if selected_feature == "⚠️ Site Risk Assessment":

        st.markdown(
            """
<div style="
    background: rgba(255, 152, 0, 0.08);
    border-left: 4px solid #FF9800;
    padding: 18px;
    border-radius: 8px;
    margin-bottom: 25px;
">

<h3 style="
    margin: 0 0 8px 0;
    color: #FFFFFF;
">
⚠️ Site Risk Assessment
</h3>

<p style="
    color: #8B949E;
    margin: 0;
    line-height: 1.6;
">
Analyze construction site conditions,
identify potential hazards and evaluate
overall project risk.
</p>

</div>
""",
            unsafe_allow_html=True
        )

        # Run the existing Site Risk Agent
        site_risk_agent.render()

    # =========================================================
    # SAFETY MANAGEMENT
    # =========================================================

    elif selected_feature == "🦺 Safety Management":

        st.markdown(
            """
<div style="
    background: rgba(0, 230, 118, 0.08);
    border-left: 4px solid #00E676;
    padding: 18px;
    border-radius: 8px;
    margin-bottom: 25px;
">

<h3 style="
    margin: 0 0 8px 0;
    color: #FFFFFF;
">
🦺 Safety Management
</h3>

<p style="
    color: #8B949E;
    margin: 0;
    line-height: 1.6;
">
Monitor worker safety, incidents,
safety compliance and overall safety performance.
</p>

</div>
""",
            unsafe_allow_html=True
        )

        # Run the existing Safety Agent
        safety_agent.render()