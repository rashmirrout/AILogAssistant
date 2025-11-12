"""
Streamlit frontend for Log Analytics Assistant.
Main application entry point.
"""

import streamlit as st
import requests
from typing import Dict, Any
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from frontend.components.sidebar import render_sidebar
from frontend.components.chat_ui import render_chat_interface
from frontend.components.context_viewer import render_context_viewer

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Log Analytics Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f5f5f5;
    }
    .reference-box {
        background-color: #fff3cd;
        padding: 0.5rem;
        border-radius: 0.3rem;
        border-left: 3px solid #ffc107;
        margin: 0.5rem 0;
    }
    .stats-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables."""
    if 'current_issue' not in st.session_state:
        st.session_state.current_issue = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'embedding_model' not in st.session_state:
        st.session_state.embedding_model = "gemini:text-embedding-004"
    if 'llm_model' not in st.session_state:
        st.session_state.llm_model = "gemini-1.5-flash"
    if 'available_models' not in st.session_state:
        try:
            response = requests.get(f"{API_BASE_URL}/models")
            if response.status_code == 200:
                st.session_state.available_models = response.json()
            else:
                st.session_state.available_models = {
                    "embedding_models": ["gemini:text-embedding-004"],
                    "llm_models": ["gemini-1.5-flash"]
                }
        except:
            st.session_state.available_models = {
                "embedding_models": ["gemini:text-embedding-004"],
                "llm_models": ["gemini-1.5-flash"]
            }

def main():
    """Main application function."""
    init_session_state()
    
    # Header
    st.markdown('<div class="main-header">🔍 Log Analytics Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered Log Analysis with RAG</div>', unsafe_allow_html=True)
    
    # Sidebar
    render_sidebar(API_BASE_URL)
    
    # Main content
    if st.session_state.current_issue:
        # Display issue info
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.info(f"📂 Current Issue: **{st.session_state.current_issue}**")
        
        with col2:
            if st.button("🔄 Refresh Stats"):
                st.rerun()
        
        # Get and display issue stats
        try:
            response = requests.get(f"{API_BASE_URL}/issue_stats/{st.session_state.current_issue}")
            if response.status_code == 200:
                stats = response.json()
                
                # Display stats in columns
                stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                
                with stat_col1:
                    st.markdown(f"""
                    <div class="stats-card">
                        <h4>📊 Chunks</h4>
                        <p style="font-size: 1.5rem; font-weight: bold;">{stats.get('chunks', 0)}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with stat_col2:
                    st.markdown(f"""
                    <div class="stats-card">
                        <h4>💬 Messages</h4>
                        <p style="font-size: 1.5rem; font-weight: bold;">{stats.get('conversation', {}).get('total_messages', 0)}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with stat_col3:
                    st.markdown(f"""
                    <div class="stats-card">
                        <h4>🤖 Embedding</h4>
                        <p style="font-size: 0.9rem;">{stats.get('embedding_model', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with stat_col4:
                    st.markdown(f"""
                    <div class="stats-card">
                        <h4>💡 LLM</h4>
                        <p style="font-size: 0.9rem;">{stats.get('llm_model_last_used', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
        except:
            pass
        
        st.divider()
        
        # Chat interface
        render_chat_interface(API_BASE_URL, st.session_state.current_issue)
        
    else:
        # Welcome message
        st.markdown("""
        ## Welcome to Log Analytics Assistant! 👋
        
        Get started by:
        1. **Creating a new issue** or **selecting an existing one** from the sidebar
        2. **Uploading log files** for analysis
        3. **Building the knowledge base** (parse logs and generate embeddings)
        4. **Asking questions** about your logs using natural language
        
        ### Features:
        - 🔍 **Semantic Search**: Find relevant log entries using natural language queries
        - 🤖 **AI-Powered Analysis**: Get insights powered by Google Gemini
        - 📊 **Context-Aware**: Retrieve and display relevant log excerpts
        - 💾 **Local Storage**: All data stored securely on your filesystem
        - 🔒 **Privacy-Focused**: No external database dependencies
        
        ### Configurable Models:
        - Choose between different embedding models (Gemini, SentenceTransformers)
        - Select your preferred LLM (Gemini 1.5 Flash or Pro)
        """)

def cli_main():
    """CLI entry point for uvx."""
    import sys
    import subprocess
    subprocess.run([sys.executable, "-m", "streamlit", "run", __file__])

if __name__ == "__main__":
    main()
