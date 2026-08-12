import streamlit as st


def dashboard_header(project):

    st.markdown(f"""
    <div style="
        background:linear-gradient(135deg,#1E3A8A,#2563EB);
        padding:30px;
        border-radius:18px;
        color:white;
        margin-bottom:20px;
    ">

    <h1 style="margin:0;">
        🏗️ ConstructIQ AI Enterprise
    </h1>

    <h2 style="margin-top:10px;">
        {project['Project_Name']}
    </h2>

    <hr style="border:1px solid rgba(255,255,255,0.3);">

    <div style="
        display:flex;
        justify-content:space-between;
        font-size:18px;
    ">

    <div>

    📍 <b>Location</b><br>
    {project['Location']}

    </div>

    <div>

    👤 <b>Manager</b><br>
    {project['Project_Manager']}

    </div>

    <div>

    🏢 <b>Client</b><br>
    {project['Client_Name']}

    </div>

    <div>

    📊 <b>Status</b><br>
    {project['Current_Status']}

    </div>

    </div>

    </div>

    """, unsafe_allow_html=True)