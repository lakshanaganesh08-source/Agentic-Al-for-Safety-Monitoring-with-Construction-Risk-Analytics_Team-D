"""
llama_client.py
----------------
Small wrapper around a locally running Llama model (served through Ollama)
so the Construction Chatbot module can send/receive messages easily.

Why Ollama?
-----------
Ollama is the simplest way to run Llama models (llama3, llama3.1, etc.)
on your own machine and expose them at http://localhost:11434.
The Streamlit app never needs an internet connection or API key for this —
it just talks to your local Ollama server.

Setup (one-time, on the machine running this app):
    1. Install Ollama:      https://ollama.com/download
    2. Pull a model:        ollama pull llama3
    3. Make sure it's up:   ollama serve   (usually starts automatically)

If Ollama isn't running, the chatbot module will show a friendly warning
and fall back to a small offline rule-based responder so the UI still works.
"""

import json
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "llama3"

# ---------------------------------------------------------------------------
# System prompt: this is what keeps the assistant "on topic".
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are "BuildBot", a construction-industry assistant embedded inside a
Construction Intelligence Hub used by site engineers, project managers and clients.

STRICT RULES YOU MUST FOLLOW:
1. Only answer questions related to construction, civil engineering, architecture,
   building materials, structural safety, project estimation, site management,
   construction law/contracts, and building codes.
2. If the user asks anything unrelated to construction (e.g. general trivia, coding,
   entertainment, politics, personal advice, other industries), politely decline and
   say you can only help with construction-related questions. Give ONE short sentence
   of decline, then ask if they have a construction question instead. Do NOT answer
   the off-topic question in any way, even partially.
3. Keep answers practical, clear, and professional — suitable for a client or engineer.
4. When giving quantities, costs, or material estimates, always mention these are
   approximate and final figures should be verified by a certified structural engineer.
5. Never invent building-code numbers you are not confident about; say so and
   recommend checking local regulations if unsure.
"""

CONSTRUCTION_KEYWORDS = [
    "construction", "cement", "concrete", "steel", "rebar", "brick", "site",
    "building", "structure", "structural", "foundation", "beam", "column",
    "slab", "roof", "wall", "plaster", "excavation", "material", "estimate",
    "estimation", "contractor", "architect", "engineer", "safety", "scaffold",
    "labour", "labor", "project", "blueprint", "plan", "permit", "code",
    "sq ft", "square feet", "sqft", "sand", "aggregate", "rcc", "masonry",
    "tile", "flooring", "electrical wiring", "plumbing", "waterproofing",
    "paint", "civil", "survey", "soil test", "load bearing", "girder",
    "truss", "cost", "budget", "quantity", "brickwork", "formwork", "curing",
    "reinforcement", "quotation", "residential", "commercial", "renovation",
    "interior", "exterior", "site visit", "inspection", "vendor", "supplier",
]


def is_probably_construction_related(text: str) -> bool:
    """Lightweight keyword guard used BEFORE hitting the LLM.
    This is a first line of defense; the system prompt is the second.
    Greetings/small talk are allowed through so the bot can respond politely."""
    text_l = text.lower()
    greetings = ["hi", "hello", "hey", "thanks", "thank you", "bye", "ok", "okay"]
    if any(g == text_l.strip(".! ") for g in greetings):
        return True
    return any(kw in text_l for kw in CONSTRUCTION_KEYWORDS)


OFF_TOPIC_REPLY = (
    "I'm BuildBot — I can only help with construction, civil engineering and "
    "site-related questions. 🏗️ Could you ask me something about your project, "
    "materials, safety, or estimation instead?"
)


def chat_with_llama(user_message: str, history: list, model: str = DEFAULT_MODEL) -> str:
    """
    Send a message to the local Llama model through Ollama's chat API.

    Parameters
    ----------
    user_message : str        The latest user message.
    history      : list[dict] Prior turns as [{"role": "user"/"assistant", "content": ...}, ...]
    model        : str        Ollama model tag (e.g. "llama3", "llama3.1", "llama3:8b")

    Returns
    -------
    str  The assistant's reply (already guardrailed for construction-only topics).
    """
    # First line of defense — obvious off-topic asks never reach the model.
    if not is_probably_construction_related(user_message):
        return OFF_TOPIC_REPLY

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.4},
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        reply = data.get("message", {}).get("content", "").strip()
        return reply if reply else OFF_TOPIC_REPLY
    except requests.exceptions.ConnectionError:
        return (
            "⚠️ I couldn't reach the local Llama server (Ollama) at "
            f"`{OLLAMA_URL}`.\n\nMake sure Ollama is installed and running:\n"
            "```\nollama serve\nollama pull llama3\n```\n"
            "Meanwhile, here's an offline fallback answer:\n\n" + offline_fallback(user_message)
        )
    except Exception as e:
        return f"⚠️ Unexpected error talking to Llama: {e}"


def offline_fallback(user_message: str) -> str:
    """A tiny rule-based responder so the UI still feels alive without Ollama running."""
    text_l = user_message.lower()
    if "cement" in text_l:
        return "As a rough thumb rule, residential RCC construction uses ~0.4 bags of cement per sq.ft. Use the Material Estimation module for a fuller breakdown."
    if "safety" in text_l:
        return "Key site safety basics: helmets, safety harnesses above 2m height, marked exclusion zones, and daily toolbox talks. See the Site Safety module for a full checklist."
    if "steel" in text_l or "rebar" in text_l:
        return "A common estimate is ~4–5 kg of steel per sq.ft for a typical G+1/G+2 residential structure, but this varies with structural design."
    return "I can help with construction topics like materials, estimation, safety, and site planning — try asking about one of those, or connect Ollama for full AI answers."
