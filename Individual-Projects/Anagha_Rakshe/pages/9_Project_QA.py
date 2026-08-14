import streamlit as st

from AI.llm import ask_llama
from AI.pdf_reader import read_pdf

from components.sidebar import show_sidebar

st.set_page_config(
    page_title="Project Q&A",
    page_icon="❓"
)

show_sidebar()

st.title("❓ Project Question & Answer")

st.markdown("""
Upload a construction project document and ask questions about it.
""")

uploaded_file = st.file_uploader(
    "Upload Project Document",
    type=["pdf"]
)

if uploaded_file:

    document_text = read_pdf(uploaded_file)

    st.success("Document Loaded Successfully")

    question = st.text_input(
        "Ask your question"
    )

    if st.button("Get Answer"):

        if question:

            prompt = f"""
You are a construction project expert.

Below is a construction project document.

Answer ONLY using the information provided.

If the answer is not available in the document,
say:

"The uploaded document does not contain this information."

----------------------

PROJECT DOCUMENT

{document_text[:8000]}

----------------------

QUESTION

{question}
"""

            with st.spinner("Searching document..."):

                answer = ask_llama(
                    prompt,
                    "You are an expert construction document assistant."
                )

            st.success("Answer")

            st.write(answer)