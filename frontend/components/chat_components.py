"""
Reusable chat message components for Claude-like UI.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, List, Optional


def render_message(
    role: str,
    content: str,
    timestamp: Optional[str] = None,
    model: Optional[str] = None,
    references: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    compact: bool = False
) -> None:
    """
    Render a chat message with Claude-like styling.
    
    Args:
        role: 'user' or 'assistant'
        content: Message content
        timestamp: ISO timestamp or formatted time
        model: Model name for assistant messages
        references: List of reference sources
        metadata: Additional metadata (chunks_retrieved, etc.)
        compact: Use compact styling
    """
    
    if role == "user":
        _render_user_message(content, timestamp, compact)
    else:
        _render_assistant_message(content, timestamp, model, references, metadata, compact)


def _render_user_message(content: str, timestamp: Optional[str], compact: bool) -> None:
    """Render user message."""
    compact_class = " compact-message" if compact else ""
    
    # Format timestamp
    time_str = _format_timestamp(timestamp) if timestamp else ""
    
    st.markdown(f"""
    <div class="message-wrapper">
        <div class="message-user{compact_class}">
            <div class="message-header">
                <span>👤 You</span>
            </div>
            <div class="message-content">
                {_escape_html(content)}
            </div>
            {f'<div class="message-footer">{time_str}</div>' if time_str else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_assistant_message(
    content: str,
    timestamp: Optional[str],
    model: Optional[str],
    references: Optional[List[str]],
    metadata: Optional[Dict[str, Any]],
    compact: bool
) -> None:
    """Render assistant message."""
    compact_class = " compact-message" if compact else ""
    
    # Format timestamp
    time_str = _format_timestamp(timestamp) if timestamp else ""
    
    # Model badge
    model_badge = ""
    if model:
        model_display = _get_model_display_name(model)
        model_badge = f'<span class="message-badge">🤖 {model_display}</span>'
    
    # Chunks retrieved badge
    chunks_badge = ""
    if metadata and metadata.get('chunks_retrieved'):
        chunks_badge = f'<span class="message-badge">🔍 {metadata["chunks_retrieved"]} chunks</span>'
    
    # Footer content
    footer_items = []
    if time_str:
        footer_items.append(time_str)
    if model_badge:
        footer_items.append(model_badge)
    if chunks_badge:
        footer_items.append(chunks_badge)
    
    footer_html = f'<div class="message-footer">{"".join(footer_items)}</div>' if footer_items else ''
    
    st.markdown(f"""
    <div class="message-wrapper">
        <div class="message-assistant{compact_class}">
            <div class="message-header">
                <span>🤖 Assistant</span>
            </div>
            <div class="message-content">
                {_escape_html(content)}
            </div>
            {footer_html}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show references if available
    if references and len(references) > 0:
        if len(references) <= 2:
            # Show inline for few references
            for ref in references:
                st.markdown(f"""
                <div class="reference-box">
                    📎 {_escape_html(ref)}
                </div>
                """, unsafe_allow_html=True)
        else:
            # Use expander for many references
            with st.expander(f"📎 References ({len(references)})"):
                for ref in references:
                    st.markdown(f"""
                    <div class="reference-box">
                        📄 {_escape_html(ref)}
                    </div>
                    """, unsafe_allow_html=True)


def render_batch_separator(text: str = "Earlier messages") -> None:
    """Render a separator between message batches."""
    st.markdown(f"""
    <div class="message-batch-separator">
        <span>{text}</span>
    </div>
    """, unsafe_allow_html=True)


def render_empty_state() -> None:
    """Render empty chat state."""
    st.markdown("""
    <div style="text-align: center; padding: 3rem 1rem; color: var(--text-muted);">
        <div style="font-size: 3rem; margin-bottom: 1rem;">💬</div>
        <div style="font-size: 1.1rem; margin-bottom: 0.5rem;">No messages yet</div>
        <div style="font-size: 0.9rem;">Start by asking a question about your logs</div>
    </div>
    """, unsafe_allow_html=True)


def render_loading_message() -> None:
    """Render loading state for assistant response."""
    st.markdown("""
    <div class="message-wrapper loading-pulse">
        <div class="message-assistant">
            <div class="message-header">
                <span>🤖 Assistant</span>
            </div>
            <div class="message-content">
                Analyzing your logs...
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _format_timestamp(timestamp: str) -> str:
    """Format timestamp for display."""
    try:
        # Try to parse ISO format
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%I:%M %p')
    except:
        # Return as-is if parsing fails
        return timestamp


def _get_model_display_name(model: str) -> str:
    """Get friendly display name for model."""
    if "flash" in model.lower():
        return "Flash"
    elif "pro" in model.lower():
        return "Pro"
    elif "gemini" in model.lower():
        return "Gemini"
    else:
        # Truncate long model names
        if len(model) > 20:
            return model[:17] + "..."
        return model


def _escape_html(text: str) -> str:
    """Escape HTML special characters but preserve newlines."""
    import html
    # Escape HTML
    text = html.escape(text)
    # Convert newlines to <br> for proper display
    text = text.replace('\n', '<br>')
    return text
