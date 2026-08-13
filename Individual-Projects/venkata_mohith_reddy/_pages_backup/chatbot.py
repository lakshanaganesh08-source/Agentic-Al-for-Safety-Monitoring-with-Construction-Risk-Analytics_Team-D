import streamlit as st
from ui_components import UIComponents
import ollama_helper

class ChatbotPage:
    """
    Renders an interactive, context-aware AI chatbot assistant (Apex Builder AI)
    which dynamically answers structural, material, and zoning queries
    based on the current simulation state.
    """
    
    @staticmethod
    def render():
        # Inject standard style components
        UIComponents.inject_global_css()
        
        st.markdown("<h2 style='margin-bottom: 20px; color: #8A2BE2 !important;'>🤖 Apex Builder AI</h2>", unsafe_allow_html=True)
        
        # Connection check on startup
        connected, conn_err = ollama_helper.check_connection()
        if connected:
            has_model, model_err = ollama_helper.check_model('llama3.2')
            if not has_model:
                st.error("⚠️ Local AI (Llama 3.2) is not running — model 'llama3.2' not found. Run `ollama pull llama3.2` and try again.")
        else:
            st.error(f"⚠️ Local AI (Llama 3.2) is not running — start Ollama and try again. (Details: {conn_err})")

        # Check if we have active results to guide context
        has_context = "analysis_results" in st.session_state and st.session_state.analysis_results is not None
        
        # Chat history initialization
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [
                {
                    "role": "assistant", 
                    "content": "Greetings! I am Apex Builder AI, your dedicated construction planning superintendent. Run a Spatial Simulation or ask me anything about material choices, zoning, spacing regulations, structural layout, or project budgets!"
                }
            ]
            
        # Layout columns
        col_chat, col_info = st.columns([2, 1], gap="large")
        
        with col_chat:
            st.markdown('<div class="glass-card neon-card-purple" style="margin-bottom: 12px;">', unsafe_allow_html=True)
            st.markdown("<h4 style='margin-top:0; color:#FFFFFF;'>💬 Conversation Terminal</h4>", unsafe_allow_html=True)
            
            # Display scrollable messages using st.chat_message
            chat_container = st.container(height=380)
            with chat_container:
                for msg in st.session_state.chat_history:
                    with st.chat_message(msg["role"]):
                        role_class = "chat-ai" if msg["role"] == "assistant" else "chat-user"
                        bubble_style = (
                            "background: rgba(138, 43, 226, 0.06); border: 1px solid rgba(138, 43, 226, 0.3); border-left: 4px solid #8A2BE2; padding: 12px 16px; border-radius: 12px;" 
                            if msg["role"] == "assistant" 
                            else "background: rgba(0, 180, 216, 0.06); border: 1px solid rgba(0, 180, 216, 0.3); border-right: 4px solid #00B4D8; padding: 12px 16px; border-radius: 12px;"
                        )
                        st.markdown(
                            f"""
                            <div class="{role_class}" style="font-size: 0.95rem; line-height: 1.45; {bubble_style}">
                                {msg['content']}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
            
            # Suggestion Chips above the input container
            st.markdown("<div style='margin-top: 10px; margin-bottom: 6px; font-size: 0.85rem; color: #a0aec0; font-weight: 500;'>💡 Quick Questions:</div>", unsafe_allow_html=True)
            chip_col1, chip_col2, chip_col3, chip_col4 = st.columns(4)
            selected_chip = None
            
            with chip_col1:
                if st.button("💰 Cost Guide", key="chip_cost", use_container_width=True):
                    selected_chip = "Estimate my material cost and structural budget."
            with chip_col2:
                if st.button("🛡️ Safety Steps", key="chip_safety", use_container_width=True):
                    selected_chip = "What safety precautions apply to this project?"
            with chip_col3:
                if st.button("🏢 Space Limits", key="chip_space", use_container_width=True):
                    selected_chip = "How can I reduce space usage to stay within zoning limits?"
            with chip_col4:
                if st.button("📐 Vertical Expansion", key="chip_expand", use_container_width=True):
                    selected_chip = "Can I vertically expand this structural model later?"
            
            # User input box (use standard st.chat_input)
            user_query = st.chat_input("Ask a construction question...")
            
            # Check if user clicked a chip or typed in the input box
            query_to_process = selected_chip if selected_chip else user_query
            
            if query_to_process:
                # Append user query to history
                st.session_state.chat_history.append({"role": "user", "content": query_to_process})
                
                # Render user query in chat_container immediately
                with chat_container:
                    with st.chat_message("user"):
                        st.markdown(
                            f"""
                            <div class="chat-msg chat-user" style="padding: 12px 16px; border-radius: 12px; font-size: 0.95rem; line-height: 1.45; background: rgba(0, 180, 216, 0.06); border: 1px solid rgba(0, 180, 216, 0.3); border-right: 4px solid #00B4D8;">
                                {query_to_process}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    
                    # Render AI response placeholder styled container
                    with st.chat_message("assistant"):
                        placeholder = st.empty()
                        
                        full_response = ""
                        if not connected:
                            full_response = "⚠️ Local AI (Llama 3.2) is not running — start Ollama and try again."
                            placeholder.markdown(full_response)
                        else:
                            context_data = st.session_state.analysis_results if has_context else None
                            
                            # Retrieve document chunks matching query if context loaded
                            doc_context = None
                            if st.session_state.get("uploaded_file_chunks"):
                                from utils.document_parser import retrieve_relevant_chunks
                                doc_context = retrieve_relevant_chunks(query_to_process, st.session_state.uploaded_file_chunks)
                                
                            # Pass history memory (last 6 messages) to maintain conversational context
                            chat_history_slice = st.session_state.chat_history[:-1]
                            
                            try:
                                stream = ollama_helper.get_chat_response_stream(query_to_process, context_data, doc_context, chat_history_slice)
                                
                                # Consume stream in batches to minimize Streamlit WebSocket update latency
                                chunk_accumulator = ""
                                for chunk in stream:
                                    full_response += chunk
                                    chunk_accumulator += chunk
                                    # Batch updates every 15 characters to keep the typing feel smooth but avoid clogging Streamlit reruns
                                    if len(chunk_accumulator) >= 15 or "\n" in chunk:
                                        placeholder.markdown(
                                            f"""
                                            <div class="chat-msg chat-ai" style="padding: 12px 16px; border-radius: 12px; font-size: 0.95rem; line-height: 1.45; background: rgba(138, 43, 226, 0.06); border: 1px solid rgba(138, 43, 226, 0.3); border-left: 4px solid #8A2BE2;">
                                                {full_response} ▌
                                            </div>
                                            """,
                                            unsafe_allow_html=True
                                        )
                                        chunk_accumulator = ""
                                
                                # Render final message without cursor
                                placeholder.markdown(
                                    f"""
                                    <div class="chat-msg chat-ai" style="padding: 12px 16px; border-radius: 12px; font-size: 0.95rem; line-height: 1.45; background: rgba(138, 43, 226, 0.06); border: 1px solid rgba(138, 43, 226, 0.3); border-left: 4px solid #8A2BE2;">
                                        {full_response}
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                            except Exception as e:
                                full_response = f"⚠️ Error communicating with Llama 3.2: {str(e)}"
                                placeholder.markdown(full_response)
                
                # Store final response in chat history and trigger rerun to refresh display loop
                st.session_state.chat_history.append({"role": "assistant", "content": full_response})
                st.rerun()
                
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_info:
            # File Uploader Card
            st.markdown('<div class="glass-card neon-card-blue" style="margin-bottom: 20px;">', unsafe_allow_html=True)
            st.markdown("<h4 style='margin-top:0; color:#FFFFFF;'>📎 Upload Project Document</h4>", unsafe_allow_html=True)
            st.write("Upload reports, specs, calculations, or guidelines to analyze their contents:")
            
            uploaded_file = st.file_uploader(
                "Choose a document",
                type=["pdf", "docx", "txt", "csv", "xlsx", "md", "json"],
                label_visibility="collapsed"
            )
            
            if uploaded_file is not None:
                # Limit size to 5MB
                max_bytes = 5 * 1024 * 1024
                if uploaded_file.size > max_bytes:
                    st.error(f"⚠️ File is too large ({uploaded_file.size / 1024 / 1024:.1f}MB). Max allowed size is 5MB.")
                else:
                    # Process file if it's a new upload
                    if st.session_state.get("uploaded_file_name") != uploaded_file.name:
                        with st.spinner("⏳ Extracting and indexing document text..."):
                            try:
                                from utils.document_parser import extract_text_from_file, chunk_text
                                file_bytes = uploaded_file.read()
                                doc_text = extract_text_from_file(uploaded_file.name, file_bytes)
                                
                                if doc_text.strip():
                                    st.session_state.uploaded_file_text = doc_text
                                    st.session_state.uploaded_file_chunks = chunk_text(doc_text)
                                    st.session_state.uploaded_file_name = uploaded_file.name
                                    st.success(f"✅ Indexed {uploaded_file.name} successfully!")
                                    st.toast(f"📄 Successfully indexed {uploaded_file.name}!", icon="✅")
                                else:
                                    st.warning("⚠️ Uploaded file appears to be empty or contains no extractable text.")
                            except Exception as e:
                                st.error(f"❌ Extraction failed: {str(e)}")
                                
                    if st.session_state.get("uploaded_file_name") == uploaded_file.name:
                        st.markdown(
                            f"""
                            <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(0, 180, 216, 0.2); padding: 10px; border-radius: 6px; font-size: 0.85rem; color: #E2E8F0;">
                                <strong>📄 Active Document:</strong> {uploaded_file.name}<br>
                                <strong>⚖️ File Size:</strong> {uploaded_file.size / 1024:.1f} KB<br>
                                <strong>🧩 Chunks Indexed:</strong> {len(st.session_state.get('uploaded_file_chunks', []))}<br>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
            else:
                # Reset session state if file was removed
                if "uploaded_file_name" in st.session_state:
                    st.session_state.pop("uploaded_file_name", None)
                    st.session_state.pop("uploaded_file_text", None)
                    st.session_state.pop("uploaded_file_chunks", None)
                    st.toast("🗑️ Document context removed.", icon="ℹ️")
            st.markdown('</div>', unsafe_allow_html=True)

            # Sidebar Tip Card
            st.markdown('<div class="glass-card" style="height: 100%;">', unsafe_allow_html=True)
            st.markdown("<h4 style='margin-top:0; color:#FFFFFF;'>💡 Pro Tips</h4>", unsafe_allow_html=True)
            st.markdown(
                """
                - **Upload structural guidelines** or zoning PDFs to chat directly with them.
                - **Run a spatial simulation** in the Space Analysis tab first to give Apex Builder AI your active model measurements, location zone, and layout calculations.
                - Apex Builder AI is running **locally on Llama 3.2** to keep your designs and data fully private.
                """
            )
            st.markdown('</div>', unsafe_allow_html=True)

# Auto-execute render function when script is run by Streamlit
ChatbotPage.render()
