import streamlit as st

from utils.guardrail import validate_query
from utils.ollama_chat import ask_llm, check_connection
from utils.prompt_builder import build_prompt
from utils.query_engine import answer_query


def show(data):

    # =====================================================
    # SESSION
    # =====================================================

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "user_query" not in st.session_state:
        st.session_state.user_query = ""

    # =====================================================
    # HEADER
    # =====================================================

    left, right = st.columns([8, 2])

    with left:

        st.title("🤖 ConstructIQ AI Assistant")

        st.caption(
            "AI-powered Construction Intelligence using Llama 3.2"
        )

    with right:

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button(
            "🗑 Clear Chat",
            use_container_width=True
        ):
            st.session_state.chat_history = []
            st.rerun()

    # =====================================================
    # OLLAMA STATUS
    # =====================================================

    if check_connection():

        st.success("🟢 Ollama Connected (Llama 3.2)")

    else:

        st.error("🔴 Ollama Not Running")

        st.info(
            "Run:\n\nollama run llama3.2"
        )

        st.stop()

    st.divider()

    # =====================================================
    # QUICK ACTIONS
    # =====================================================

    st.subheader("⚡ Quick Actions")

    questions = [

        "Portfolio Summary",
        "Highest Budget",
        "Budget Utilization",

        "Delay Analysis",
        "Rework Summary",
        "Safety Status",

        "Risk Analysis",
        "Pending Documents",
        "Daily Reports"

    ]

    for i in range(0, len(questions), 3):

        cols = st.columns(3)

        for j in range(3):

            if i + j < len(questions):

                if cols[j].button(
                    questions[i+j],
                    use_container_width=True
                ):

                    st.session_state.user_query = questions[i+j]

                    st.rerun()

    st.divider()

    # =====================================================
    # CHAT HISTORY
    # =====================================================

    st.subheader("💬 Conversation")

    if not st.session_state.chat_history:

        st.info(
"""
👋 Welcome to ConstructIQ AI

Ask a project-related question to get started.
"""
        )

    for role, message in st.session_state.chat_history:

        with st.chat_message(role):

            st.markdown(message)

    # =====================================================
    # CHAT INPUT
    # =====================================================

    query = st.chat_input(
        "Ask ConstructIQ AI..."
    )

    if st.session_state.user_query:

        query = st.session_state.user_query

        st.session_state.user_query = ""

    # =====================================================
    # PROCESS QUERY
    # =====================================================

    if query:

        st.session_state.chat_history.append(
            ("user", query)
        )

        with st.spinner(
            "Analyzing project data..."
        ):

            # --------------------------------------------
            # Guardrail
            # --------------------------------------------

            valid, result = validate_query(query)

            if not valid:

                response = result

            elif result == "greeting":

                response = (
                    "Hello! 👋\n\n"
                    "I'm ConstructIQ AI.\n\n"
                    "I can help you analyze:\n\n"
                    "• Projects\n"
                    "• Budget & Cost\n"
                    "• Material Estimation\n"
                    "• Delays\n"
                    "• Rework\n"
                    "• Safety\n"
                    "• Risks\n"
                    "• Documents\n"
                    "• Daily Reports\n\n"
                    "How can I assist you with your construction project today?"
                )

            else:

                analytics = answer_query(query, data)

                if analytics:

                    prompt = f"""
Construction analytics generated the following result.

{analytics}

User Question:

{query}

Explain the result professionally.

Requirements:

• Use bullet points.

• Keep the answer concise.

• Give one practical recommendation.

Do not invent information.
"""

                    response = ask_llm(prompt)

                else:

                    prompt = build_prompt(
                        query,
                        data
                    )

                    response = ask_llm(prompt)

        st.session_state.chat_history.append(

            ("assistant", response)

        )

        st.rerun()

    # =====================================================
    # FOOTER
    # =====================================================

    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Projects",
            len(data["projects"])
        )

    with c2:

        st.metric(
            "Documents",
            len(data["documents"])
        )

    with c3:

        st.metric(
            "Safety Records",
            len(data["safety"])
        )

    with c4:

        st.metric(
            "AI Model",
            "Llama 3.2"
        )

    st.caption(
        "ConstructIQ AI Enterprise • AI-powered Construction Project Management Platform"
    )