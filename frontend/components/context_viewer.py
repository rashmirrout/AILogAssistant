"""
Context viewer component for displaying retrieved log chunks.
"""

import streamlit as st
from typing import List, Dict, Any

def render_context_viewer(context_chunks: List[Dict[str, Any]]):
    """
    Render context chunks with syntax highlighting and metadata.
    
    Args:
        context_chunks: List of chunk dictionaries
    """
    if not context_chunks:
        st.info("No context chunks to display")
        return
    
    st.subheader(f"📋 Retrieved Context ({len(context_chunks)} chunks)")
    
    for idx, chunk in enumerate(context_chunks):
        with st.expander(f"📄 Chunk {idx + 1}: {chunk.get('source_file', 'Unknown')} (lines {chunk.get('start_line', '?')}-{chunk.get('end_line', '?')})"):
            # Display metadata
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.caption(f"**File:** {chunk.get('source_file', 'N/A')}")
            with col2:
                st.caption(f"**Lines:** {chunk.get('start_line', '?')}-{chunk.get('end_line', '?')}")
            with col3:
                if chunk.get('timestamp_range'):
                    st.caption(f"**Time Range:** ✓")
            
            # Display chunk text
            st.code(chunk.get('text', ''), language='log')
            
            # Display timestamp range if available
            if chunk.get('timestamp_range'):
                ts_range = chunk['timestamp_range']
                st.caption(f"⏰ {ts_range[0]} → {ts_range[1]}")
