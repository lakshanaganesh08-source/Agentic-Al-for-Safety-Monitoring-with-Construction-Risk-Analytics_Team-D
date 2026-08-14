import streamlit as st

from AI.llm import ask_llama
from AI.prompts import DOCUMENT_ANALYSIS_PROMPT
from AI.pdf_reader import read_pdf

from components.sidebar import show_sidebar
st.set_page_config(page_title="Construction Documentation Analysis", page_icon="📄")

show_sidebar()
st.title("📄 Construction Documentation Analysis")


st.markdown("""
Upload a construction document (PDF) to analyze it using AI.

The AI will provide:

- 📋 Executive Summary
- ⚠️ Risk Identification
- ❗ Missing Information
- 💡 Recommendations
""")

uploaded_file = st.file_uploader(
    "Upload Construction Document",
    type=["pdf"]
)

if uploaded_file:

    st.success(f"Uploaded: {uploaded_file.name}")

    with st.spinner("Reading PDF..."):

        document_text = read_pdf(uploaded_file)

    with st.expander("📖 View Extracted Text"):

        st.write(document_text[:5000])

    if st.button("🔍 Analyze Document"):

        with st.spinner("AI is analyzing the document..."):

            response = ask_llama(
                document_text,
                DOCUMENT_ANALYSIS_PROMPT
            )

        st.success("Analysis Complete")

        st.subheader("🤖 AI Analysis")

        with st.container(border=True):
            st.markdown(response)