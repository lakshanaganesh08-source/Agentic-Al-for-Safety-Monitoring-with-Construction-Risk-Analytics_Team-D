import streamlit as st
from utils.ollama_client import (
    DEFAULT_MODEL as OLLAMA_MODEL,
    check_ollama_connection,
    generate_with_ollama,
    build_chat_prompt,
    list_ollama_models,
)
from utils.construction_classifier import (
    classify_query,
    get_construction_fallback_response,
    SECTION_8_SYSTEM_PROMPT as SYSTEM_PROMPT,
)
from utils.styling import page_hero

INITIAL_GREETING = (
    "Hello! I am your Construction Intelligence Assistant 🏗️. "
    "I can help with construction, civil engineering, building design, infrastructure, site safety, quantity surveying, "
    "and construction technology-related questions. What would you like to know?"
)


def render():
    connected, checked_host = check_ollama_connection()
    status_color = "#00E676" if connected else "#FF5252"
    status_text = "Connected" if connected else "Offline"

    available_models = list_ollama_models() if connected else [OLLAMA_MODEL]

    page_hero(
        "💬", "Construction Intelligence Assistant",
        f"Expert AI assistant for construction, civil engineering &amp; infrastructure powered by Llama 3.2 (<code style='color:#00E5FF;'>{OLLAMA_MODEL}</code>)",
        badge="CONSTRUCTION INTELLIGENCE ONLY"
    )

    dot_html = '<span class="hub-pulse-dot"></span>' if connected else ""
    st.markdown(f"""
        <div class="hub-card" style="margin-bottom: 22px; padding: 16px 18px;">
            <div style='display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px;'>
                <div style='min-width: 270px;'>
                    <p style='margin: 0; color: #F0F6FC; font-weight: 600;'>Construction Intelligence Assistant · Strict 2-Pass Classification &amp; Fail-Closed Guardrails</p>
                    <p style='margin: 6px 0 0 0; color: #8B949E; font-size: 0.85rem;'>Llama 3.2 Engine at <code>{checked_host}</code></p>
                </div>
                <div class="hub-pill" style='background: {status_color}22; color: {status_color}; border: 1px solid {status_color}55;'>
                    {dot_html} {status_text}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### ⚙️ Engine Settings")
        selected_model = st.selectbox(
            "Model",
            available_models,
            index=0 if OLLAMA_MODEL in available_models else 0,
            key="general_model",
        )
        response_style = st.selectbox(
            "Answer style",
            ["Fastest", "Fast", "Balanced", "Detailed"],
            index=2,
            key="general_speed",
        )
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    style_settings = {
        "Fastest": {"max_tokens": 80, "temperature": 0.3, "suffix": "Answer in one short sentence."},
        "Fast": {"max_tokens": 150, "temperature": 0.3, "suffix": "Keep the answer short and direct, under 50 words."},
        "Balanced": {"max_tokens": 250, "temperature": 0.5, "suffix": "Keep the answer concise, practical, and clear."},
        "Detailed": {"max_tokens": 450, "temperature": 0.7, "suffix": "Provide a helpful, detailed answer with formulas/examples where applicable."},
    }
    selected_params = style_settings.get(response_style, style_settings["Balanced"])

    # Ensure message state is initialized
    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state.messages = [{"role": "assistant", "content": INITIAL_GREETING}]
    elif "history, science, writing, code" in st.session_state.messages[0].get("content", ""):
        st.session_state.messages[0] = {"role": "assistant", "content": INITIAL_GREETING}

    if len(st.session_state.messages) <= 1:
        st.markdown("<p style='color: #8B949E; font-weight: 700; font-size: 0.8rem; letter-spacing: 0.6px;'>SUGGESTED QUESTIONS</p>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        prompt_to_submit = None
        with col1:
            if st.button("📐 Concrete Volume Calculation", use_container_width=True):
                prompt_to_submit = "How do I calculate concrete volume?"
            if st.button("🧱 What is BOQ?", use_container_width=True):
                prompt_to_submit = "What is BOQ?"
        with col2:
            if st.button("🏛️ Types of Foundations", use_container_width=True):
                prompt_to_submit = "What are the different types of foundations?"
            if st.button("💻 What is BIM?", use_container_width=True):
                prompt_to_submit = "What is BIM?"
        with col3:
            if st.button("💰 Cost Estimation Methods", use_container_width=True):
                prompt_to_submit = "How is construction cost estimated?"
            if st.button("🦺 Site Safety Practices", use_container_width=True):
                prompt_to_submit = "What are construction site safety practices?"
    else:
        prompt_to_submit = None

    for message in st.session_state.messages:
        avatar = "🙋" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    user_input = st.chat_input("Ask a construction or civil engineering question...")

    if prompt_to_submit or user_input:
        prompt = prompt_to_submit if prompt_to_submit else user_input

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🙋"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            message_placeholder = st.empty()

            # 2-Pass Classification & Security Guardrail
            history = st.session_state.messages[:-1]
            tag, override_response = classify_query(prompt, history=history, model=selected_model)

            if override_response:
                message_placeholder.markdown(override_response)
                st.session_state.messages.append({"role": "assistant", "content": override_response})
            else:
                # LLM Execution with Section 8 System Prompt
                full_prompt = build_chat_prompt(
                    f"{SYSTEM_PROMPT}\n\n{selected_params['suffix']}",
                    history,
                    prompt,
                )

                with st.spinner("Consulting Construction Intelligence Assistant..."):
                    full_response, success = generate_with_ollama(
                        full_prompt,
                        model=selected_model,
                        max_tokens=selected_params["max_tokens"],
                        temperature=selected_params["temperature"],
                    )

                if success:
                    message_placeholder.markdown(full_response)
                else:
                    # Smart Fallback for valid construction questions when Ollama server is offline
                    fallback_answer = get_construction_fallback_response(prompt)
                    message_placeholder.markdown(fallback_answer)
                    full_response = fallback_answer

                st.session_state.messages.append({"role": "assistant", "content": full_response})
