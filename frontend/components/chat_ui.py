"""
Chat interface component.
"""

import streamlit as st
import requests

def render_chat_interface(api_base_url: str, issue_id: str):
    """
    Render the chat interface for querying logs.
    
    Args:
        api_base_url: Base URL for API requests
        issue_id: Current issue ID
    """
    st.subheader("💬 Chat with Your Logs")
    
    # Load chat history
    try:
        response = requests.get(f"{api_base_url}/chat_history/{issue_id}")
        if response.status_code == 200:
            history_data = response.json()
            st.session_state.chat_history = history_data.get('history', [])
    except:
        pass
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        if st.session_state.chat_history:
            for msg in st.session_state.chat_history:
                if msg['role'] == 'user':
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>👤 You:</strong><br>
                        {msg['message']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <strong>🤖 Assistant:</strong><br>
                        {msg['message']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show references if available
                    if msg.get('references'):
                        with st.expander("📎 References"):
                            for ref in msg['references']:
                                st.markdown(f"""
                                <div class="reference-box">
                                    📄 {ref}
                                </div>
                                """, unsafe_allow_html=True)
                    
                    # Show context chunks if available
                    if msg.get('metadata', {}).get('chunks_retrieved'):
                        st.caption(f"🔍 Retrieved {msg['metadata']['chunks_retrieved']} relevant chunks")
        else:
            st.info("💡 No messages yet. Start by asking a question about your logs!")
    
    st.divider()
    
    # Query input
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_query = st.text_input(
            "Ask a question about your logs:",
            placeholder="e.g., What errors occurred in the last hour?",
            key="query_input",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("🚀 Send", use_container_width=True)
    
    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        top_k = st.slider(
            "Number of chunks to retrieve",
            min_value=1,
            max_value=20,
            value=5,
            help="More chunks = more context but slower response"
        )
        
        use_custom_llm = st.checkbox("Use different LLM for this query")
        custom_llm = None
        if use_custom_llm:
            available_models = st.session_state.get('available_models', {})
            llm_models = available_models.get('llm_models', ['gemini-1.5-flash'])
            custom_llm = st.selectbox("Select LLM", llm_models)
    
    # Handle query submission
    if send_button and user_query:
        with st.spinner("🔍 Analyzing logs..."):
            try:
                response = requests.post(
                    f"{api_base_url}/query",
                    json={
                        "issue_id": issue_id,
                        "query": user_query,
                        "top_k": top_k,
                        "llm_model": custom_llm if use_custom_llm else st.session_state.llm_model
                    }
                )
                
                if response.status_code == 200:
                    st.success("✅ Response generated!")
                    st.rerun()
                elif response.status_code == 400:
                    st.error("❌ " + response.json().get('detail', 'Please build the knowledge base first'))
                else:
                    st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Clear history button
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat History", key="clear_history"):
            st.warning("This will clear all chat history. This action cannot be undone.")
            # Note: Would need to implement clear endpoint in backend
