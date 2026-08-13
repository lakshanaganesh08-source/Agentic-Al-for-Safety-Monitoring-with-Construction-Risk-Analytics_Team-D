import time
import streamlit as st
from utils.ollama_client import (
    DEFAULT_MODEL as OLLAMA_MODEL,
    FAST_TIMEOUT,
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
        "🏗️", "Construction Expert",
        "Construction Intelligence Assistant with strict 2-layer domain guardrails and conversation memory",
        badge="CONSTRUCTION INTELLIGENCE ONLY"
    )

    dot_html = '<span class="hub-pulse-dot"></span>' if connected else ""
    st.markdown(f"""
        <div class="hub-card" style="margin-bottom: 22px; padding: 14px 18px;">
            <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;'>
                <span style='color:#8B949E; font-size:0.88rem;'>Ollama · {checked_host} · {len(available_models)} model(s)</span>
                <div class="hub-pill" style='background: {status_color}22; color: {status_color}; border: 1px solid {status_color}55;'>
                    {dot_html} {status_text}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if "construction_messages" not in st.session_state or not st.session_state.construction_messages:
        st.session_state.construction_messages = [
            {"role": "assistant", "content": INITIAL_GREETING}
        ]

    with st.sidebar:
        selected_model = st.selectbox("Model", available_models, key="construction_model")
        detail_level = st.selectbox("Detail", ["Brief", "Standard", "Detailed"], index=1, key="construction_detail")
        if st.button("🗑️ Clear Construction Chat", use_container_width=True):
            st.session_state.construction_messages = []
            st.rerun()

    detail_settings = {
        "Brief": {"max_tokens": 80, "suffix": "Answer in under 40 words."},
        "Standard": {"max_tokens": 180, "suffix": "Give a clear, practical answer."},
        "Detailed": {"max_tokens": 320, "suffix": "Provide a detailed answer with steps or standards where applicable."},
    }
    params = detail_settings[detail_level]

    if len(st.session_state.construction_messages) <= 1:
        st.markdown("<p style='color: #8B949E; font-weight: 700; font-size: 0.8rem;'>QUICK QUESTIONS</p>", unsafe_allow_html=True)
        q1, q2, q3 = st.columns(3)
        quick_prompt = None
        with q1:
            if st.button("🦺 OSHA PPE rules", use_container_width=True):
                quick_prompt = "What PPE is required on an active construction site per OSHA?"
        with q2:
            if st.button("🧱 Concrete curing", use_container_width=True):
                quick_prompt = "How long should concrete cure before loading?"
        with q3:
            if st.button("📋 Cost Estimation & BOQ", use_container_width=True):
                quick_prompt = "How is construction cost estimated?"
    else:
        quick_prompt = None

    for msg in st.session_state.construction_messages:
        avatar = "👷" if msg["role"] == "user" else "🏗️"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask a construction or civil engineering question...")
    prompt = quick_prompt or user_input
    if not prompt:
        return

    st.session_state.construction_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👷"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🏗️"):
        placeholder = st.empty()
        start = time.time()

        # Layer 1: Classification & Security Guardrails
        history = st.session_state.construction_messages[:-1]
        tag, override_response = classify_query(prompt, history=history, model=selected_model)

        if override_response:
            full_response = override_response
            placeholder.markdown(full_response)
        else:
            # Layer 2: Send query to Llama 3.2
            full_prompt = build_chat_prompt(
                f"{SYSTEM_PROMPT}\n\n{params['suffix']}",
                history,
                prompt,
            )
            with st.spinner("Consulting construction knowledge base..."):
                full_response, success = generate_with_ollama(
                    full_prompt,
                    model=selected_model,
                    max_tokens=params["max_tokens"],
                    temperature=0.2,
                    timeout=FAST_TIMEOUT,
                )
            if success:
                placeholder.markdown(full_response)
            else:
                fallback_answer = get_construction_fallback_response(prompt)
                placeholder.markdown(fallback_answer)
                full_response = fallback_answer

        elapsed = time.time() - start
        st.caption(f"⏱ {elapsed:.2f}s")

    st.session_state.construction_messages.append({"role": "assistant", "content": full_response})
