import time
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

# --- What makes this bot different from the general one -------------------
# 1. It never leaves construction. A cheap local keyword pass runs BEFORE any
#    network call, so a clearly off-topic question ("write me a poem about
#    the ocean") gets rejected in milliseconds instead of round-tripping to
#    the model.
# 2. Even when a question passes the check, the model call is tuned for
#    speed (low max_tokens, temperature 0, short system prompt) so on-topic
#    answers come back fast rather than "up to 20 seconds" like a generic
#    detailed response.
CONSTRUCTION_KEYWORDS = {
    "construction", "site", "osha", "safety", "ppe", "hardhat", "scaffold",
    "concrete", "curing", "rebar", "framing", "foundation", "excavation",
    "hvac", "electrical", "plumbing", "permit", "code", "inspection",
    "contractor", "subcontractor", "blueprint", "structural", "steel",
    "roofing", "drywall", "grading", "survey", "material", "budget",
    "schedule", "delay", "crane", "demolition", "welding", "insulation",
    "cement", "masonry", "asphalt", "grout", "beam", "column", "load",
    "zoning", "building", "worksite", "jobsite", "labor", "welfare",
    "equipment", "backfill", "pour", "formwork", "shoring", "trench",
}

SYSTEM_PROMPT = (
    "You are a construction-only assistant. Answer ONLY questions about "
    "construction, building codes, site safety, materials, scheduling, or "
    "project management. Be brief and direct."
)


def is_construction_related(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in CONSTRUCTION_KEYWORDS)


def check_ollama_connection():
    for root_url in OLLAMA_ROOT_URLS:
        try:
            r = requests.get(root_url, timeout=2)
            if r.status_code == 200:
                return True, root_url
        except requests.RequestException:
            continue
    return False, OLLAMA_ROOT_URLS[0]


def request_ollama(payload):
    last_exc = None
    for url in OLLAMA_API_URLS:
        try:
            return requests.post(url, json=payload, timeout=(3, 15)), url
        except requests.RequestException as exc:
            last_exc = exc
            continue
    raise last_exc or RuntimeError("Unable to reach Ollama on any configured host.")


def render():
    connected, checked_host = check_ollama_connection()
    status_color = "#00E676" if connected else "#FF5252"
    status_text = "Connected" if connected else "Offline"

    page_hero(
        "🏗️", "Construction Assistant",
        "Construction topics only, tuned to answer in under a second.",
        badge="SITE-SCOPED · FAST"
    )

    dot_html = '<span class="hub-pulse-dot"></span>' if connected else ""
    st.markdown(f"""
        <div class="hub-card" style="margin-bottom: 22px; padding: 14px 18px;">
            <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;'>
                <span style='color:#8B949E; font-size:0.88rem;'>Local Ollama · <code>{OLLAMA_MODEL}</code> · {checked_host}</span>
                <div class="hub-pill" style='background: {status_color}22; color: {status_color}; border: 1px solid {status_color}55;'>
                    {dot_html} {status_text}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if "construction_messages" not in st.session_state:
        st.session_state.construction_messages = [
            {"role": "assistant", "content": "I only answer construction questions -- OSHA/PPE, curing times, scheduling, materials, codes, etc. Ask away."}
        ]

    with st.sidebar:
        if st.button("🗑️ Clear Construction Chat", width="stretch"):
            st.session_state.construction_messages = []
            st.rerun()

    for msg in st.session_state.construction_messages:
        avatar = "👷" if msg["role"] == "user" else "🏗️"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask a construction question...")
    if not user_input:
        return

    st.session_state.construction_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👷"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🏗️"):
        placeholder = st.empty()
        start = time.time()

        if not is_construction_related(user_input):
            full_response = (
                "That's outside construction topics, so I can't help with it here. "
                "Try the **General Assistant** page instead, or ask me something "
                "about site safety, materials, scheduling, or codes."
            )
            placeholder.markdown(full_response)
        else:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": f"{SYSTEM_PROMPT}\n\nQuestion: {user_input}\nAnswer in under 30 words:",
                "max_tokens": 60,
                "temperature": 0.0,
                "stream": False,
            }
            try:
                response, _ = request_ollama(payload)
                if response.status_code == 200:
                    result = response.json()
                    full_response = result.get("response") or result.get("text") or "No response received."
                else:
                    full_response = f"⚠️ Ollama error (status {response.status_code})"
                placeholder.markdown(full_response)
            except requests.exceptions.ConnectionError:
                full_response = "❌ Could not connect to Ollama. Run `ollama run llama3.2` in a terminal."
                placeholder.error(full_response)
            except requests.Timeout:
                full_response = "⏳ Timed out -- try again."
                placeholder.warning(full_response)
            except Exception as e:
                full_response = f"⚠️ Unexpected error: {e}"
                placeholder.error(full_response)

        elapsed = time.time() - start
        st.caption(f"⏱ {elapsed:.2f}s")

    st.session_state.construction_messages.append({"role": "assistant", "content": full_response})
