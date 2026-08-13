import numpy as np
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.styling import hero, section_label
from utils.data_gen import generate_faq_data

GREETING_WORDS = {"hi", "hello", "hey", "hola", "good morning", "good evening"}


@st.cache_resource(show_spinner=False)
def _build_index():
    faqs = generate_faq_data()
    questions = [q for q, a in faqs]
    answers = [a for q, a in faqs]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(questions)
    return vectorizer, matrix, questions, answers


def _answer_query(query: str, df: pd.DataFrame):
    vectorizer, matrix, questions, answers = _build_index()

    q_lower = query.lower().strip()

    if any(w in q_lower for w in ["how many project", "total project", "number of project"]):
        return f"There are currently **{len(df)}** projects tracked in the portfolio."
    if "over budget" in q_lower or ("overrun" in q_lower and "project" in q_lower):
        n = (df["cost_overrun_pct"] > 10).sum()
        return f"**{n}** projects are currently more than 10% over budget."
    if "delay" in q_lower and ("how many" in q_lower or "which project" in q_lower or "high risk" in q_lower):
        n = (df["delay_risk"] == "High").sum()
        return f"**{n}** projects are currently classified as **High** delay risk by the AI model."
    if "average ppe" in q_lower or ("ppe" in q_lower and "average" in q_lower):
        return f"The portfolio's average PPE compliance is **{df['ppe_compliance'].mean()*100:.1f}%**."
    if "safety incident" in q_lower and ("rate" in q_lower or "how many" in q_lower):
        n = df["safety_incident"].sum()
        return f"There have been **{n}** recorded safety incidents across all tracked projects."
    if "total budget" in q_lower or "portfolio budget" in q_lower:
        return f"The total portfolio budget is **₹{df['budget'].sum()/1e7:.2f} Cr**."

    q_vec = vectorizer.transform([query])
    sims = cosine_similarity(q_vec, matrix)[0]
    best_idx = int(np.argmax(sims))
    best_score = sims[best_idx]

    if best_score < 0.15:
        return (
            "I'm not fully certain about that one. I can help with **cost predictions**, "
            "**delay risk**, **safety analytics**, the **computer vision scanner**, or "
            "**report generation**. Could you rephrase your question?"
        )
    return answers[best_idx]


def render(df: pd.DataFrame):
    hero(
        "CIH Assistant",
        "An NLP-powered chatbot using TF-IDF vectorization and cosine similarity to answer "
        "questions about your projects and how the platform works.",
        badge="GENERATIVE AI",
    )

    section_label("CHAT WITH THE AI ASSISTANT")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": (
                "👋 Hello! I'm **CIH Assistant**. Ask me about project costs, delay risk, "
                "safety, the computer vision scanner, or how any module works."
            )}
        ]

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👷"):
            st.markdown(msg["content"])

    suggestions = [
        "How many projects are over budget?",
        "How does the cost overrun prediction work?",
        "How can I improve site safety?",
        "What is PPE compliance?",
    ]
    st.write("")
    cols = st.columns(len(suggestions))
    clicked = None
    for c, s in zip(cols, suggestions):
        if c.button(s, use_container_width=True):
            clicked = s

    user_input = st.chat_input("Ask CIH Assistant about your construction portfolio...")
    query = clicked or user_input

    if query:
        st.session_state.chat_history.append({"role": "user", "content": query})
        answer = _answer_query(query, df)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    with st.expander("⚙️ How this chatbot works (technical notes)"):
        st.markdown(
            "- Questions are matched against a curated FAQ knowledge base using **TF-IDF** "
            "vectorization and **cosine similarity**.\n"
            "- A set of intents (e.g. *'how many projects are over budget'*) are answered "
            "directly from the **live project dataset** rather than static text.\n"
            "- Low-confidence matches trigger a graceful fallback instead of a hallucinated answer."
        )
