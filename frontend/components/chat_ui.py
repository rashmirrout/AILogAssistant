"""
Chat interface component with Claude-like design.
"""

import streamlit as st
import requests
from typing import Dict, Any, List
from datetime import datetime
from frontend.components.chat_components import (
    render_message,
    render_batch_separator,
    render_empty_state,
    render_loading_message
)

# Constants
MESSAGES_PER_BATCH = 15
BATCH_LOAD_INCREMENT = 10

def render_chat_interface(api_base_url: str, issue_id: str):
    """
    Render the chat interface for querying logs with Claude-like UI.
    
    Args:
        api_base_url: Base URL for API requests
        issue_id: Current issue ID
    """
    
    # Initialize session state
    _init_chat_state()
    
    # Load chat history if not already loaded
    if not st.session_state.get('chat_loaded', False):
        _load_chat_history(api_base_url, issue_id)
        st.session_state.chat_loaded = True
    
    # Header with controls and status
    col1, col2, col3, col4 = st.columns([2.5, 0.8, 0.8, 0.8])
    
    with col1:
        st.markdown("### 💬 Chat with Your Logs")
    
    with col2:
        compact_mode = st.checkbox("Compact", value=st.session_state.get('compact_mode', False))
        st.session_state.compact_mode = compact_mode
    
    with col3:
        # Show processing indicator if query is in progress
        if st.session_state.get('query_in_progress', False):
            st.markdown("⏳ **Processing**")
        else:
            st.write("")
    
    with col4:
        if st.button("🔄 Refresh"):
            st.session_state.chat_loaded = False
            st.rerun()
    
    st.divider()
    
    # Input composer at TOP
    _render_input_composer(api_base_url, issue_id)
    
    st.divider()
    
    # Display chat messages below input (newest first)
    _render_chat_history(st.session_state.chat_history, compact_mode)

def _init_chat_state():
    """Initialize chat-related session state."""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'messages_to_show' not in st.session_state:
        st.session_state.messages_to_show = MESSAGES_PER_BATCH
    if 'compact_mode' not in st.session_state:
        st.session_state.compact_mode = False
    if 'show_advanced' not in st.session_state:
        st.session_state.show_advanced = False
    if 'chat_loaded' not in st.session_state:
        st.session_state.chat_loaded = False
    if 'query_in_progress' not in st.session_state:
        st.session_state.query_in_progress = False
    if 'input_key' not in st.session_state:
        st.session_state.input_key = 0

def _load_chat_history(api_base_url: str, issue_id: str):
    """Load chat history from backend."""
    try:
        response = requests.get(f"{api_base_url}/chat_history/{issue_id}")
        if response.status_code == 200:
            history_data = response.json()
            st.session_state.chat_history = history_data.get('history', [])
    except Exception as e:
        st.error(f"Error loading chat history: {str(e)}")

def _render_chat_history(history: List[Dict[str, Any]], compact: bool):
    """Render chat message history with batching - newest first (descending order)."""
    
    if not history:
        render_empty_state()
        return
    
    # Determine how many messages to show (from the end, newest first)
    total_messages = len(history)
    messages_to_show = min(st.session_state.messages_to_show, total_messages)
    start_idx = max(0, total_messages - messages_to_show)
    
    # Get visible messages and reverse them (newest first)
    visible_messages = list(reversed(history[start_idx:]))
    
    # Render visible messages (newest to oldest)
    for msg in visible_messages:
        role = msg.get('role', 'assistant')
        content = msg.get('message', '')
        timestamp = msg.get('timestamp')
        
        # Extract metadata for assistant messages
        model = None
        references = None
        metadata = None
        
        if role == 'assistant':
            model = msg.get('model')
            references = msg.get('references')
            metadata = msg.get('metadata', {})
        
        render_message(
            role=role,
            content=content,
            timestamp=timestamp,
            model=model,
            references=references,
            metadata=metadata,
            compact=compact
        )
    
    # Show "Load older messages" button at the bottom if there are more messages
    if start_idx > 0:
        st.divider()
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(f"📜 Show {min(BATCH_LOAD_INCREMENT, start_idx)} older messages", use_container_width=True):
                st.session_state.messages_to_show += BATCH_LOAD_INCREMENT
                st.rerun()
        
        st.caption(f"💡 {start_idx} earlier messages hidden")

def _render_input_composer(api_base_url: str, issue_id: str):
    """Render the input composer with send functionality."""
    
    # Advanced options toggle
    col1, col2 = st.columns([6, 1])
    
    with col1:
        st.write("")  # Spacer
    
    with col2:
        if st.button("⚙️" if not st.session_state.show_advanced else "✕", key="toggle_advanced"):
            st.session_state.show_advanced = not st.session_state.show_advanced
            st.rerun()
    
    # Show advanced options if toggled
    if st.session_state.show_advanced:
        st.markdown('<div class="floating-panel">', unsafe_allow_html=True)
        st.markdown("**Advanced Options**")
        
        top_k = st.slider(
            "Chunks to retrieve",
            min_value=1,
            max_value=20,
            value=5,
            key="adv_top_k",
            help="More chunks = more context but slower"
        )
        
        use_custom_llm = st.checkbox("Use different LLM", key="adv_use_custom")
        custom_llm = None
        if use_custom_llm:
            available_models = st.session_state.get('available_models', {})
            llm_models = available_models.get('llm_models', ['gemini-1.5-flash'])
            custom_llm = st.selectbox("Select LLM", llm_models, key="adv_custom_llm")
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Default values when advanced is hidden
        top_k = 5
        custom_llm = None
    
    # Query input area - improved sizing with dynamic key for clearing
    user_query = st.text_area(
        "Ask a question about your logs",
        placeholder="e.g., What errors occurred in the last hour?",
        key=f"query_input_{st.session_state.input_key}",
        label_visibility="collapsed",
        height=100,
        disabled=st.session_state.get('query_in_progress', False)
    )
    
    # Send and Cancel buttons - better layout
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.caption("💡 Type your question above and click Send")
    
    with col2:
        # Cancel button if query in progress
        if st.session_state.get('query_in_progress', False):
            if st.button("❌ Cancel", key="cancel_btn", use_container_width=True):
                st.session_state.query_in_progress = False
                st.session_state.input_key += 1  # Clear input
                st.warning("⚠️ Request cancelled")
                st.rerun()
        else:
            st.write("")
    
    with col3:
        send_button = st.button(
            "🚀 Send", 
            key="send_btn", 
            use_container_width=True, 
            type="primary",
            disabled=st.session_state.get('query_in_progress', False)
        )
    
    # Handle query submission
    if send_button and user_query.strip():
        _handle_query_submission(
            api_base_url,
            issue_id,
            user_query,
            top_k,
            custom_llm if st.session_state.get('show_advanced') and st.session_state.get('adv_use_custom') else st.session_state.llm_model
        )

def _handle_query_submission(
    api_base_url: str,
    issue_id: str,
    query: str,
    top_k: int,
    llm_model: str
):
    """Handle query submission to backend with animated progress."""
    
    # Set processing flag
    st.session_state.query_in_progress = True
    
    # Create containers for animated progress
    progress_placeholder = st.empty()
    
    try:
        # Show animated progress with skeleton
        with progress_placeholder:
            st.markdown("""
            <div style="margin: 2rem 0;">
                <div class="animated-progress-bar">
                    <div class="progress-bar-fill"></div>
                </div>
                <div style="text-align: center; margin-top: 1rem; color: var(--text-secondary);">
                    <span class="loading-pulse">🔍 Analyzing logs and generating response...</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show skeleton assistant message
            st.markdown("""
            <div class="message-wrapper skeleton-loading">
                <div class="message-assistant">
                    <div class="message-header">
                        <span>🤖 Assistant</span>
                    </div>
                    <div class="skeleton-text"></div>
                    <div class="skeleton-text" style="width: 80%;"></div>
                    <div class="skeleton-text" style="width: 60%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Make the API request
        response = requests.post(
            f"{api_base_url}/query",
            json={
                "issue_id": issue_id,
                "query": query,
                "top_k": top_k,
                "llm_model": llm_model
            },
            timeout=120
        )
        
        # Clear progress indicators
        progress_placeholder.empty()
        
        if response.status_code == 200:
            # Clear input and reset state
            st.session_state.query_in_progress = False
            st.session_state.input_key += 1  # Increment to clear input
            st.session_state.messages_to_show = MESSAGES_PER_BATCH
            st.session_state.chat_loaded = False
            
            st.success("✅ Response generated!")
            st.rerun()
            
        elif response.status_code == 400:
            st.session_state.query_in_progress = False
            error_detail = response.json().get('detail', 'Please build the knowledge base first')
            st.error(f"❌ {error_detail}")
        else:
            st.session_state.query_in_progress = False
            st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
    
    except requests.Timeout:
        progress_placeholder.empty()
        st.session_state.query_in_progress = False
        st.error("❌ Request timed out (120s). The query took too long.")
    except Exception as e:
        progress_placeholder.empty()
        st.session_state.query_in_progress = False
        st.error(f"❌ Error: {str(e)}")
