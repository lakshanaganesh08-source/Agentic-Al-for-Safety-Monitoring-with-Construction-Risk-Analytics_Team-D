import streamlit as st


import streamlit as st

def metric_card(title, value, icon, color, subtitle=""):

    st.markdown(
        f"""
<div style="
background:white;
padding:20px;
border-radius:15px;
border-left:6px solid {color};
">
<h4>{icon} {title}</h4>
<h2 style="color:{color};">{value}</h2>
<p>{subtitle}</p>
</div>
""",
        unsafe_allow_html=True,
    )
def status_card(title, status, color):

    html = f"""
    <div style="
        background:white;
        border-radius:18px;
        padding:20px;
        text-align:center;
        box-shadow:0 6px 15px rgba(0,0,0,.08);
    ">
        <h4 style="color:#1E293B;">{title}</h4>

        <h2 style="color:{color};">
            {status}
        </h2>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)


def info_card(title, content):

    html = f"""
    <div style="
        background:white;
        border-radius:18px;
        padding:20px;
        box-shadow:0 6px 15px rgba(0,0,0,.08);
    ">

        <h4 style="color:#1E3A8A;">
            {title}
        </h4>

        <p style="
            color:#475569;
            line-height:1.8;
            font-size:15px;
        ">
            {content}
        </p>

    </div>
    """

    st.markdown(html, unsafe_allow_html=True)