import streamlit as st
from utils.llama_client import chat_with_llama, DEFAULT_MODEL


def render():
    st.markdown(
        """<div class="page-header">
        <h1>💬 Construction Chatbot (BuildBot)</h1>
        <p>Powered by a locally-running Llama model — answers <b>construction questions only</b>.</p>
        </div>""",
        unsafe_allow_html=True,
    )

    with st.expander("ℹ️ About this chatbot"):
        st.write(
            "BuildBot is connected to a local Llama model through **Ollama**. "
            "It is restricted so it will only discuss construction, civil engineering, "
            "materials, safety, and project-related topics — any off-topic question "
            "(general trivia, other subjects, etc.) will be politely declined."
        )
        model = st.text_input("Ollama model tag", value=DEFAULT_MODEL, key="chat_model_tag")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Render existing conversation
    for msg in st.session_state.chat_history:
        css_class = "chat-bubble-user" if msg["role"] == "user" else "chat-bubble-bot"
        align = "flex-end" if msg["role"] == "user" else "flex-start"
        st.markdown(
            f'<div style="display:flex; justify-content:{align};">'
            f'<div class="{css_class}">{msg["content"]}</div></div>',
            unsafe_allow_html=True,
        )

    user_input = st.chat_input("Ask a construction question (materials, safety, cost, timeline...)")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.markdown(
            f'<div style="display:flex; justify-content:flex-end;">'
            f'<div class="chat-bubble-user">{user_input}</div></div>',
            unsafe_allow_html=True,
        )

        with st.spinner("BuildBot is thinking..."):
            history_for_model = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.chat_history[:-1]
            ]
            reply = chat_with_llama(
                user_input, history=history_for_model, model=st.session_state.get("chat_model_tag", DEFAULT_MODEL)
            )

        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.markdown(
            f'<div style="display:flex; justify-content:flex-start;">'
            f'<div class="chat-bubble-bot">{reply}</div></div>',
            unsafe_allow_html=True,
        )

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
