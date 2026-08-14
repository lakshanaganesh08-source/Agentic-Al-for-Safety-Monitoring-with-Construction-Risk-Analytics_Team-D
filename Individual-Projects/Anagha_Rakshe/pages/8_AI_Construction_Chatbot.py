import streamlit as st

from AI.llm import ask_llama
from AI.prompts import CHATBOT_PROMPT
from AI.knowledge_base import PROJECT_KNOWLEDGE
from components.sidebar import show_sidebar

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="Construction AI Assistant",
    page_icon="🤖",
    layout="wide"
)

show_sidebar()

# -------------------------------------------------
# PAGE HEADER
# -------------------------------------------------

st.title("🤖 Construction Intelligence Hub AI Assistant")

st.success("""
Welcome to the **Construction Intelligence Hub AI Assistant**.

I am an AI-powered assistant that specializes in answering questions related to:

🏗 Construction Management

📄 Document Analysis

⚠ Risk Detection

🦺 Site Safety

🧱 Material Estimation

📝 Daily Reports

👷 Workforce Management

📊 Dashboard

❓ Construction Intelligence Hub

💻 Technologies Used
""")

st.divider()

# -------------------------------------------------
# SAMPLE QUESTIONS
# -------------------------------------------------

st.subheader("💡 Try asking")

col1, col2 = st.columns(2)

with col1:
    st.info("""
• What is Construction Intelligence Hub?

• How much cement is required for a 3-floor building?

• How many workers are needed for a G+3 building?

• Explain Risk Detection.

• Explain Site Safety.
""")

with col2:
    st.info("""
• What is M25 concrete?

• Explain Material Estimation.

• Explain Document Analysis.

• What technologies are used?

• Explain the Dashboard.
""")

st.divider()

# -------------------------------------------------
# CHAT HISTORY
# -------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -------------------------------------------------
# CHAT INPUT
# -------------------------------------------------

prompt = st.chat_input("Ask a construction-related question...")

if prompt:

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # ---------------------------------------------
    # RETRIEVE RELEVANT KNOWLEDGE
    # ---------------------------------------------

    full_prompt = f"""
PROJECT KNOWLEDGE

{PROJECT_KNOWLEDGE}

====================================================

USER QUESTION

{prompt}

====================================================

Instructions:

1. Decide whether the user's question is related to construction, civil engineering, building construction, construction management, or the Construction Intelligence Hub.

2. If YES:
   - Answer professionally.
   - Use the PROJECT KNOWLEDGE whenever relevant.
   - If the answer is not present in the PROJECT KNOWLEDGE, use your own construction engineering knowledge.

3. For estimation questions such as:
   - Cement quantity
   - Steel quantity
   - Brick quantity
   - Concrete quantity
   - Sand quantity
   - Aggregate quantity
   - Number of workers
   - Labour requirement
   - Construction cost
   - Building duration

   Provide a practical approximate estimate and clearly mention that actual values depend on structural drawings, soil conditions, local building codes, project specifications, and engineering design.

4. Never refuse genuine construction questions simply because they are not explicitly mentioned in the project knowledge.

5. If the question is unrelated to construction or the Construction Intelligence Hub, reply with the refusal message defined in the system prompt.
"""

    with st.spinner("🤖 Llama 3.2 is thinking..."):
        response = ask_llama(
            full_prompt,
            CHATBOT_PROMPT
        )

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

# -------------------------------------------------
# CLEAR CHAT
# -------------------------------------------------

st.divider()

if st.button("🗑 Clear Conversation"):
    st.session_state.messages = []
    st.rerun()

st.divider()

st.caption(
    "🏗️ Construction Intelligence Hub | Powered by Llama 3.2 • Ollama • Streamlit | Infosys Springboard Internship 7.0"
)