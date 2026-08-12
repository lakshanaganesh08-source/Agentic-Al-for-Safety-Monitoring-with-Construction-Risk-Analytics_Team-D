import streamlit as st

import config
from utils.data_loader import load_data
from utils.session import initialize_session


def show_sidebar():
    """Display the application sidebar."""

    initialize_session()

    data = load_data()
    projects = data["projects"]

    with st.sidebar:

        # =====================================================
        # LOGO
        # =====================================================

        try:
            st.image(config.LOGO_PATH, width=190)
        except:
            pass

        st.markdown(f"## 🏗️ {config.APP_NAME}")
        st.caption(config.APP_TAGLINE)

        st.divider()

        # =====================================================
        # COMPANY DETAILS
        # =====================================================

        st.subheader("🏢 Company")

        st.write(config.COMPANY_NAME)

        st.metric(
            label="Active Projects",
            value=len(projects)
        )

        st.divider()

        # =====================================================
        # PROJECT SELECTOR
        # =====================================================

        project_names = projects["Project_Name"].tolist()

        default_index = 0

        if st.session_state.selected_project_name in project_names:
            default_index = project_names.index(
                st.session_state.selected_project_name
            )

        selected_project_name = st.selectbox(
            "📂 Select Project",
            options=project_names,
            index=default_index
        )

        selected_row = projects[
            projects["Project_Name"] == selected_project_name
        ].iloc[0]

        st.session_state.selected_project = selected_row["Project_ID"]
        st.session_state.selected_project_name = selected_row["Project_Name"]

        st.info(
            f"""
**Project ID:** {selected_row['Project_ID']}

**Location:** {selected_row['Location']}

**Manager:** {selected_row['Project_Manager']}

**Status:** {selected_row['Current_Status']}
"""
        )

        st.divider()

        # =====================================================
        # NAVIGATION
        # =====================================================

        st.subheader("📂 Modules")

        pages = [
            "🏠 Dashboard",
            "📁 Project Management",
            "🧠 Executive AI Dashboard",
            "💰 Cost Estimation",
            "🧱 Material Estimation",
            "⏳ Delay Prediction",
            "🔧 Construction Rework",
            "⚠️ Risk Intelligence",
            "📝 Daily Reports",
            "💬 AI Chatbot",
            "📄 Executive Report"
        ]

        selected_page = st.radio(
            "Navigation",
            pages,
            label_visibility="collapsed"
        )

        st.session_state.current_page = selected_page

        st.divider()

        # =====================================================
        # AI STATUS
        # =====================================================

        st.subheader("🤖 AI Status")

        if st.session_state.ollama_status == "🟢 Connected":
            st.success(st.session_state.ollama_status)
        else:
            st.error(st.session_state.ollama_status)

        st.divider()

        # =====================================================
        # USER
        # =====================================================

        user = st.session_state.user

        st.markdown(f"""
        ### 👤 {user['name']}

        **Role:** {user['role']}            """)

        if st.button(
            "Logout",
            use_container_width=True
        ):

            st.session_state.logged_in = False
            st.session_state.user = None

            st.rerun()

        # =====================================================
        # VERSION
        # =====================================================

        st.caption(
            f"""
**ConstructIQ AI**

Version {config.VERSION}

Infosys Springboard 2026
"""
        )