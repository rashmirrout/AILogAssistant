"""
Streamlit frontend for Log Analytics Assistant.
Main application entry point with Claude-like UI.
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
from frontend.styles.theme import get_custom_css

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Log Analytics Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"  # Sidebar visible by default
)

# Apply custom CSS theme
st.markdown(get_custom_css(), unsafe_allow_html=True)

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
    
    # Sidebar (can be toggled with arrow button in top-left corner)
    render_sidebar(API_BASE_URL)
    
    # Help text for sidebar toggle (only show if no issue selected)
    if not st.session_state.current_issue:
        st.markdown("""
        <div style="position: fixed; top: 1rem; left: 1rem; background: var(--bg-accent); 
                    padding: 0.5rem 1rem; border-radius: var(--radius-md); 
                    border: 1px solid var(--border-accent); z-index: 999; font-size: 0.85rem;">
            💡 <strong>Tip:</strong> Use the <strong>></strong> arrow in the top-left to show/hide the Control Panel
        </div>
        """, unsafe_allow_html=True)
    
    # Main content area
    if st.session_state.current_issue:
        # Issue info header
        _render_issue_header(API_BASE_URL, st.session_state.current_issue)
        
        st.divider()
        
        # Chat interface (main content)
        render_chat_interface(API_BASE_URL, st.session_state.current_issue)
        
    else:
        # Welcome screen
        _render_welcome_screen()

def _render_issue_header(api_base_url: str, issue_id: str):
    """Render compact issue information header with badge stats."""
    
    # Get stats
    stats = {}
    try:
        response = requests.get(f"{api_base_url}/issue_stats/{issue_id}")
        if response.status_code == 200:
            stats = response.json()
    except:
        pass
    
    # Compact header with inline badges
    chunks = stats.get('chunks', 0)
    messages = stats.get('conversation', {}).get('total_messages', 0)
    embedding = stats.get('embedding_model', 'N/A')
    llm = stats.get('llm_model_last_used', 'N/A')
    
    # Shorten model names for badges
    if 'gemini' in embedding.lower():
        embedding = 'Gemini'
    elif len(embedding) > 15:
        embedding = embedding[:12] + '...'
    
    if 'flash' in llm.lower():
        llm = 'Flash'
    elif 'pro' in llm.lower():
        llm = 'Pro'
    elif len(llm) > 15:
        llm = llm[:12] + '...'
    
    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: space-between; 
                padding: 0.75rem 1rem; background: var(--bg-secondary); 
                border-radius: var(--radius-md); margin-bottom: 1rem;">
        <div style="display: flex; align-items: center; gap: 0.75rem; flex: 1;">
            <span style="font-size: 1.2rem;">📂</span>
            <span style="font-weight: 600; color: var(--text-primary);">{issue_id}</span>
            <span class="message-badge">📊 {chunks}</span>
            <span class="message-badge">💬 {messages}</span>
            <span class="message-badge">🤖 {embedding}</span>
            <span class="message-badge">💡 {llm}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def _render_welcome_screen():
    """Render welcome screen when no issue is selected."""
    st.markdown("""
    <div class="welcome-card">
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 3.5rem; margin-bottom: 1rem;">🔍</div>
            <h1 style="color: var(--text-primary); margin-bottom: 0.5rem;">
                Log Analytics Assistant
            </h1>
            <p style="color: var(--text-secondary); font-size: 1.1rem;">
                AI-Powered Log Analysis with RAG
            </p>
        </div>
        
        <div style="background: var(--bg-secondary); padding: 1.5rem; border-radius: var(--radius-md); margin-bottom: 2rem;">
            <h3 style="color: var(--text-primary); margin-bottom: 1rem;">🚀 Get Started</h3>
            <ol style="color: var(--text-primary); line-height: 1.8;">
                <li><strong>Create or select an issue</strong> from the sidebar</li>
                <li><strong>Upload log files</strong> for analysis</li>
                <li><strong>Build the knowledge base</strong> (parse logs and generate embeddings)</li>
                <li><strong>Ask questions</strong> about your logs using natural language</li>
            </ol>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
            <div style="background: var(--bg-secondary); padding: 1rem; border-radius: var(--radius-md);">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🔍</div>
                <h4 style="color: var(--text-primary); margin-bottom: 0.5rem;">Semantic Search</h4>
                <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 0;">
                    Find relevant log entries using natural language queries
                </p>
            </div>
            
            <div style="background: var(--bg-secondary); padding: 1rem; border-radius: var(--radius-md);">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🤖</div>
                <h4 style="color: var(--text-primary); margin-bottom: 0.5rem;">AI-Powered</h4>
                <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 0;">
                    Get insights powered by Google Gemini or custom models
                </p>
            </div>
            
            <div style="background: var(--bg-secondary); padding: 1rem; border-radius: var(--radius-md);">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📊</div>
                <h4 style="color: var(--text-primary); margin-bottom: 0.5rem;">Context-Aware</h4>
                <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 0;">
                    Retrieve and display relevant log excerpts with context
                </p>
            </div>
            
            <div style="background: var(--bg-secondary); padding: 1rem; border-radius: var(--radius-md);">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🔒</div>
                <h4 style="color: var(--text-primary); margin-bottom: 0.5rem;">Privacy-Focused</h4>
                <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 0;">
                    All data stored securely on your local filesystem
                </p>
            </div>
        </div>
        
        <div style="background: var(--bg-accent); padding: 1rem; border-radius: var(--radius-md); border: 1px solid var(--border-accent);">
            <p style="color: var(--text-primary); font-size: 0.9rem; margin: 0;">
                <strong>💡 Tip:</strong> You can choose between different embedding models and LLMs in the sidebar to optimize for speed or accuracy.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def cli_main():
    """CLI entry point for uvx."""
    import sys
    import subprocess
    subprocess.run([sys.executable, "-m", "streamlit", "run", __file__])

if __name__ == "__main__":
    main()
