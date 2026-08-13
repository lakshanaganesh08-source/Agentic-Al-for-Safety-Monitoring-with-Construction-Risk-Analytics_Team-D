import streamlit as st
import os

# MUST BE THE FIRST STREAMLIT CALL
st.set_page_config(
    page_title="Construction Intelligence Hub | AI Control Center",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Start background companion API server to link the HTML dashboard chatbot to Ollama
import ollama_helper
ollama_helper.start_background_server()

# Render the main full-screen control center
import pathlib
template_path = pathlib.Path("templates/control_center.html")
if template_path.exists():
    # Read original HTML template
    html_content = template_path.read_text(encoding="utf-8")
    
    # Resolve the active backend API port
    active_port = ollama_helper.get_active_port()
    
    # Dynamically inject the active port variable directly to make iframe requests 100% robust
    html_content = html_content.replace(
        "var companionApiPort = 8502;",
        f"var companionApiPort = {active_port};"
    )
    
    # Save the injected HTML to a rendered template file
    rendered_path = pathlib.Path("templates/control_center_rendered.html")
    rendered_path.write_text(html_content, encoding="utf-8")
    
    # 1. Inject parent CSS to override iframe sizing and hide Streamlit default elements
    st.markdown("""
        <style>
        header, footer, [data-testid="stHeader"], [data-testid="stDecoration"], [data-testid="stToolbar"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
        }
        div[data-testid="stSidebar"], div[data-testid="stSidebarNav"] {
            display: none !important;
            width: 0 !important;
        }
        .main .block-container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
            height: 100vh !important;
            overflow: hidden !important;
        }
        div[data-testid="stIframe"] iframe,
        div[data-testid="stHtml"] iframe,
        .element-container iframe {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            z-index: 999999 !important;
            border: none !important;
            background-color: #030308 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    import streamlit.components.v1 as components
    # 2. Serve the rendered HTML file directly inside the Streamlit component iframe
    components.html(html_content, height=1000, scrolling=False)
else:
    st.error("Error: templates/control_center.html template file not found!")
