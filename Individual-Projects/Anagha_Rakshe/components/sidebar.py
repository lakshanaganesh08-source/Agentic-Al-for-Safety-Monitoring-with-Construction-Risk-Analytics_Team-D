import streamlit as st
from datetime import datetime


def show_sidebar():

    with st.sidebar:

        st.markdown(
            """
            <h2 style='text-align:center;'>
            🏗️ Construction Intelligence Hub
            </h2>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")

        # AI Status
        st.success("🟢 AI Online")

        st.metric(
            label="AI Model",
            value="Llama 3.2"
        )

        st.metric(
            label="AI Engine",
            value="Ollama"
        )

        st.metric(
            label="Framework",
            value="Streamlit"
        )

        st.metric(
            label="Version",
            value="Milestone 2"
        )

        st.markdown("---")

        st.subheader("🚀 AI Modules")

        modules = [
            "🤖 AI Chatbot",
            "📄 Document Analysis",
            "❓ Project Q&A",
            "⚠️ Risk Detection",
            "🦺 Site Safety",
            "🧱 Material Estimation",
            "📝 Daily Reports"
        ]

        for module in modules:
            st.markdown(f"✅ {module}")

        st.markdown("---")

        st.subheader("📊 Project Overview")

        st.progress(100)

        st.caption("Development Progress")

        st.metric(
            "Completed Modules",
            "7 / 7"
        )

        st.metric(
            "AI Features",
            "7"
        )

        st.metric(
            "Status",
            "Ready"
        )

        st.markdown("---")

        st.subheader("📅 Today")

        st.write(datetime.now().strftime("%d %B %Y"))

        st.write(datetime.now().strftime("%I:%M %p"))

        st.markdown("---")

        st.info(
            """
💡 **Presentation Tip**

Use the sidebar to quickly navigate through the AI-powered construction modules.
"""
        )

        st.markdown("---")

        st.caption(
            "Built using ❤️ Python • Streamlit • Ollama • Llama 3.2"
        )

        st.caption(
            "Infosys Springboard Internship 7.0"
        )