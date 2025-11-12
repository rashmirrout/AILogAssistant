"""
Sidebar component for issue management and model selection.
"""

import streamlit as st
import requests
from datetime import datetime

def render_sidebar(api_base_url: str):
    """
    Render the sidebar with issue management and model selection.
    
    Args:
        api_base_url: Base URL for API requests
    """
    with st.sidebar:
        st.title("⚙️ Control Panel")
        
        # Model Selection Section
        st.subheader("🤖 Model Configuration")
        
        # Get available models
        available_models = st.session_state.get('available_models', {
            "embedding_models": ["gemini:text-embedding-004"],
            "llm_models": ["gemini-1.5-flash"]
        })
        
        # Embedding model selector
        embedding_models = available_models.get('embedding_models', [])
        embedding_labels = {
            "gemini:text-embedding-004": "Gemini (Cloud, 768d)",
            "st:all-MiniLM-L6-v2": "MiniLM (Local, Fast, 384d)",
            "st:all-mpnet-base-v2": "MPNet (Local, Accurate, 768d)"
        }
        
        embedding_options = [embedding_labels.get(m, m) for m in embedding_models]
        selected_embedding_idx = 0
        if st.session_state.embedding_model in embedding_models:
            selected_embedding_idx = embedding_models.index(st.session_state.embedding_model)
        
        selected_embedding = st.selectbox(
            "Embedding Model",
            options=embedding_options,
            index=selected_embedding_idx,
            help="Model used to generate embeddings for log chunks"
        )
        
        # Update session state
        for model, label in embedding_labels.items():
            if label == selected_embedding and model in embedding_models:
                st.session_state.embedding_model = model
                break
        
        # LLM model selector
        llm_models = available_models.get('llm_models', [])
        
        # Create friendly labels for all model types
        def get_llm_label(model: str) -> str:
            """Generate friendly label for LLM model."""
            if model.startswith("gemini-"):
                if "flash" in model:
                    return f"Gemini {model.replace('gemini-', '').upper()} (Fast)"
                elif "pro" in model:
                    return f"Gemini {model.replace('gemini-', '').upper()} (Accurate)"
                else:
                    return f"Gemini {model.replace('gemini-', '')}"
            elif model.startswith("openrouter:"):
                provider_model = model.replace("openrouter:", "")
                return f"OpenRouter: {provider_model}"
            elif model.startswith("azure:"):
                deployment = model.replace("azure:", "")
                return f"Azure OpenAI: {deployment}"
            else:
                return model
        
        # Build options with labels mapped back to original models
        llm_options = [(get_llm_label(m), m) for m in llm_models]
        llm_labels_display = [label for label, _ in llm_options]
        
        selected_llm_idx = 0
        if st.session_state.llm_model in llm_models:
            selected_llm_idx = llm_models.index(st.session_state.llm_model)
        
        selected_llm_display = st.selectbox(
            "LLM Model",
            options=llm_labels_display,
            index=selected_llm_idx,
            help="Model used to generate responses"
        )
        
        # Update session state - find the actual model name from the display label
        for label, model in llm_options:
            if label == selected_llm_display:
                st.session_state.llm_model = model
                break
        
        st.divider()
        
        # Issue Management Section
        st.subheader("📁 Issue Management")
        
        # Create new issue
        with st.expander("➕ Create New Issue"):
            new_issue_id = st.text_input(
                "Issue ID",
                placeholder="e.g., ISSUE-2024-001",
                key="new_issue_input"
            )
            
            if st.button("Create Issue", key="create_issue_btn"):
                if new_issue_id:
                    try:
                        response = requests.post(
                            f"{api_base_url}/create_issue",
                            json={"issue_id": new_issue_id}
                        )
                        
                        if response.status_code == 200:
                            st.success(f"✅ Issue '{new_issue_id}' created!")
                            st.session_state.current_issue = new_issue_id
                            st.rerun()
                        else:
                            st.error(f"❌ {response.json().get('detail', 'Error creating issue')}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Please enter an issue ID")
        
        # Select existing issue
        try:
            response = requests.get(f"{api_base_url}/list_issues")
            if response.status_code == 200:
                issues = response.json().get('issues', [])
                
                if issues:
                    st.write("**Select Issue:**")
                    current_idx = 0
                    if st.session_state.current_issue in issues:
                        current_idx = issues.index(st.session_state.current_issue)
                    
                    selected_issue = st.selectbox(
                        "Available Issues",
                        options=issues,
                        index=current_idx,
                        key="issue_selector",
                        label_visibility="collapsed"
                    )
                    
                    if selected_issue != st.session_state.current_issue:
                        st.session_state.current_issue = selected_issue
                        st.rerun()
                else:
                    st.info("No issues yet. Create one above!")
        except Exception as e:
            st.error(f"❌ Error loading issues: {str(e)}")
        
        st.divider()
        
        # File Upload Section (only if issue selected)
        if st.session_state.current_issue:
            st.subheader("📤 Upload Logs")
            
            uploaded_files = st.file_uploader(
                "Choose log files",
                accept_multiple_files=True,
                type=['log', 'txt', 'jsonl'],
                key="file_uploader"
            )
            
            if uploaded_files:
                if st.button("Upload Files", key="upload_btn"):
                    try:
                        files = [
                            ("files", (file.name, file.getvalue(), file.type))
                            for file in uploaded_files
                        ]
                        
                        response = requests.post(
                            f"{api_base_url}/upload_logs/{st.session_state.current_issue}",
                            files=files
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            st.success(f"✅ Uploaded {data['data']['count']} files")
                        else:
                            st.error(f"❌ Upload failed: {response.json().get('detail')}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            
            st.divider()
            
            # Knowledge Base Section
            st.subheader("🧠 Knowledge Base")
            
            force_rebuild = st.checkbox(
                "Force Rebuild",
                help="Rebuild even if embeddings exist"
            )
            
            if st.button("🔨 Build/Update KB", key="update_kb_btn", use_container_width=True):
                with st.spinner("Processing logs and building embeddings..."):
                    try:
                        response = requests.post(
                            f"{api_base_url}/update_kb",
                            json={
                                "issue_id": st.session_state.current_issue,
                                "embedding_model": st.session_state.embedding_model,
                                "force": force_rebuild
                            }
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            st.success(f"✅ KB updated! {data['data']['chunks']} chunks processed")
                            st.info(f"📐 Using: {data['data']['embedding_model']}")
                        else:
                            st.error(f"❌ {response.json().get('detail', 'Error updating KB')}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            
            st.caption("⚠️ Build KB after uploading logs to enable queries")
        
        st.divider()
        
        # Footer
        st.caption("---")
        st.caption("💡 **Tip**: Change models before building KB")
        st.caption(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
