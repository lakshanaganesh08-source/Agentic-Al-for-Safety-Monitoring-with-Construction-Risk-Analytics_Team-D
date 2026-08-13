import streamlit as st
import requests
from utils.styling import page_hero

OLLAMA_API_URLS = [
    "http://127.0.0.1:11434/api/generate",
    "http://localhost:11434/api/generate",
]
OLLAMA_MODEL = "llama3.2"
OLLAMA_ROOT_URLS = [
    "http://127.0.0.1:11434",
    "http://localhost:11434",
]


def check_ollama_connection():
    for root_url in OLLAMA_ROOT_URLS:
        try:
            response = requests.get(root_url, timeout=2)
            if response.status_code == 200:
                return True, root_url
        except requests.RequestException:
            continue
    return False, OLLAMA_ROOT_URLS[0]


def request_ollama(payload):
    last_exception = None
    for url in OLLAMA_API_URLS:
        try:
            return requests.post(url, json=payload, timeout=(5, 60)), url
        except requests.RequestException as exc:
            last_exception = exc
            continue
    raise last_exception or RuntimeError("Unable to reach Ollama on any configured host.")


def render():
    connected, checked_host = check_ollama_connection()
    status_color = "#00E676" if connected else "#FF5252"
    status_text = "Connected" if connected else "Offline"

    page_hero(
        "💬", "General AI Assistant",
        f"Ask me anything! Powered by Local Ollama (<code style='color:#00E5FF;'>{OLLAMA_MODEL}</code>)",
        badge="UNRESTRICTED · GENERAL PURPOSE"
    )

    dot_html = '<span class="hub-pulse-dot"></span>' if connected else ""
    st.markdown(f"""
        <div class="hub-card" style="margin-bottom: 22px; padding: 16px 18px;">
            <div style='display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px;'>
                <div style='min-width: 270px;'>
                    <p style='margin: 0; color: #F0F6FC; font-weight: 600;'>General Purpose · Ask me anything on any topic</p>
                    <p style='margin: 6px 0 0 0; color: #8B949E; font-size: 0.85rem;'>Local Ollama HTTP API at <code>{checked_host}/api/generate</code></p>
                    <p style='margin: 4px 0 0 0; color: #8B949E; font-size: 0.8rem;'>Responses may take up to 20 seconds depending on local model latency.</p>
                </div>
                <div class="hub-pill" style='background: {status_color}22; color: {status_color}; border: 1px solid {status_color}55;'>
                    {dot_html} {status_text}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### ⚙️ Engine Status")
        st.markdown(f"""
            <div class="hub-card" style="padding: 12px; margin-bottom: 15px;">
                <span style="color: #00E676;">● Active Engine:</span> <b>Ollama (General Purpose)</b><br>
                <span style="color: #8B949E; font-size: 0.85rem;">Model: <code>{OLLAMA_MODEL}</code></span>
            </div>
        """, unsafe_allow_html=True)

        if st.button("🗑️ Clear Chat History", width="stretch"):
            st.session_state.messages = []
            st.rerun()

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I'm your General AI Assistant. I can help with anything - ask me about history, science, writing, code, construction, cooking, entertainment, or literally any topic! 🚀"
            }
        ]

    if len(st.session_state.messages) <= 1:
        st.markdown("<p style='color: #8B949E; font-weight: 700; font-size: 0.8rem; letter-spacing: 0.6px;'>QUICK TOPICS</p>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)

        prompt_to_submit = None
        with col1:
            if st.button("🌍 Tell me about Mars", width="stretch"):
                prompt_to_submit = "Tell me 3 interesting facts about Mars."
        with col2:
            if st.button("📚 Explain Machine Learning", width="stretch"):
                prompt_to_submit = "Explain machine learning in simple terms."
        with col3:
            if st.button("🍕 Suggest a dinner idea", width="stretch"):
                prompt_to_submit = "What's a healthy dinner idea for tonight?"
    else:
        prompt_to_submit = None

    response_style = st.selectbox(
        "Answer speed",
        ["Fastest", "Fast", "Balanced", "Detailed"],
        index=1,
        help="Fastest answers are the shortest and return fastest; Detailed answers may take longer.",
        key="general_speed"
    )

    style_settings = {
        "Fastest": {"max_tokens": 40, "temperature": 0.3, "prompt_suffix": "Answer in one short sentence."},
        "Fast": {"max_tokens": 80, "temperature": 0.3, "prompt_suffix": "Keep the answer extremely short and direct, within 25 words."},
        "Balanced": {"max_tokens": 160, "temperature": 0.5, "prompt_suffix": "Keep the answer concise and clear."},
        "Detailed": {"max_tokens": 260, "temperature": 0.7, "prompt_suffix": "Provide a helpful, detailed answer with examples."},
    }
    selected_params = style_settings.get(response_style, style_settings["Fast"])

    for message in st.session_state.messages:
        avatar = "🙋" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    user_input = st.chat_input("Ask me anything...")

    if prompt_to_submit or user_input:
        prompt = prompt_to_submit if prompt_to_submit else user_input

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🙋"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            message_placeholder = st.empty()
            full_response = ""

            payload = {
                "model": OLLAMA_MODEL,
                "prompt": (
                    f"You are a helpful general-purpose AI assistant. {selected_params['prompt_suffix']}\n"
                    f"User Query: {prompt}"
                ),
                "max_tokens": selected_params["max_tokens"],
                "temperature": selected_params["temperature"],
                "stream": False
            }

            try:
                with st.spinner("Generating answer from Ollama..."):
                    response, used_url = request_ollama(payload)

                if response.status_code == 200:
                    result = response.json()
                    full_response = (
                        result.get("response")
                        or result.get("text")
                        or result.get("output")
                        or "No response received from Ollama."
                    )
                    message_placeholder.markdown(full_response)
                else:
                    try:
                        error_result = response.json()
                        full_response = error_result.get("error", f"⚠️ **Ollama Service Error** (Status Code: `{response.status_code}`)")
                    except Exception:
                        full_response = f"⚠️ **Ollama Service Error** (Status Code: `{response.status_code}`)"
                    message_placeholder.error(full_response)

            except requests.exceptions.ConnectionError:
                full_response = (
                    "❌ **Connection Failed**: Could not connect to the local Ollama server. "
                    "Make sure `ollama run llama3.2` is running in a separate terminal."
                )
                message_placeholder.error(full_response)
            except requests.Timeout:
                full_response = (
                    "⏳ **Timeout**: Connection timed out while connecting to Ollama server. "
                    "Try restarting Ollama or verify the server is listening on port `11434`."
                )
                message_placeholder.warning(full_response)
            except Exception as e:
                full_response = f"⚠️ **Unexpected Error**: `{str(e)}`"
                message_placeholder.error(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})
