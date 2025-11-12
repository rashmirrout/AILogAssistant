"""
Theme and styling configuration for Claude-like UI.
"""

def get_custom_css() -> str:
    """Return custom CSS for Claude-style interface."""
    return """
    <style>
    /* CSS Variables */
    :root {
        --bg-primary: #ffffff;
        --bg-secondary: #f8f9fa;
        --bg-tertiary: #fbfbfd;
        --bg-accent: #eef5ff;
        --bg-user: #ffffff;
        --bg-assistant: #f5f5f5;
        --bg-hover: #fafafa;
        
        --border-color: #e5e7eb;
        --border-light: #f0f0f0;
        --border-accent: #3b82f6;
        
        --text-primary: #1a1a1a;
        --text-secondary: #667085;
        --text-muted: #9ca3af;
        
        --radius-sm: 6px;
        --radius-md: 12px;
        --radius-lg: 16px;
        
        --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04);
        --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
        --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);
        
        --spacing-xs: 0.25rem;
        --spacing-sm: 0.5rem;
        --spacing-md: 1rem;
        --spacing-lg: 1.5rem;
        --spacing-xl: 2rem;
    }
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .main {
        background: linear-gradient(to bottom, #ffffff 0%, #f6f7f9 100%);
        max-width: 1400px;
        margin: 0 auto;
        padding: 0 var(--spacing-lg);
    }
    
    /* Hide Streamlit branding but keep functional controls */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Keep header visible for sidebar toggle and settings menu */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    
    /* Optionally hide "Deploy" button if present */
    button[kind="header"] {
        display: none !important;
    }
    
    /* Chat Container */
    .chat-container {
        max-width: 900px;
        margin: 0 auto;
        padding: var(--spacing-md) 0;
    }
    
    /* Message Styles - Claude-like */
    .message-wrapper {
        margin-bottom: var(--spacing-lg);
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .message-user {
        background: var(--bg-user);
        border-left: 4px solid var(--border-accent);
        border-radius: var(--radius-md);
        padding: var(--spacing-lg);
        box-shadow: var(--shadow-sm);
        margin-bottom: var(--spacing-md);
    }
    
    .message-assistant {
        background: var(--bg-assistant);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: var(--spacing-lg);
        transition: all 0.2s ease;
    }
    
    .message-assistant:hover {
        background: var(--bg-hover);
        box-shadow: var(--shadow-sm);
    }
    
    .message-header {
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
        margin-bottom: var(--spacing-sm);
        font-weight: 600;
        color: var(--text-primary);
    }
    
    .message-content {
        color: var(--text-primary);
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    .message-footer {
        display: flex;
        align-items: center;
        gap: var(--spacing-md);
        margin-top: var(--spacing-sm);
        font-size: 0.75rem;
        color: var(--text-muted);
    }
    
    .message-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        padding: 0.15rem 0.5rem;
        background: var(--bg-accent);
        border-radius: var(--radius-sm);
        font-size: 0.7rem;
        font-weight: 500;
        color: var(--border-accent);
    }
    
    /* Input Composer */
    .input-composer {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: var(--spacing-lg);
        box-shadow: var(--shadow-sm);
        margin-bottom: var(--spacing-lg);
    }
    
    .stTextInput input {
        border-radius: var(--radius-md) !important;
        border: 2px solid var(--border-color) !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput input:focus {
        border-color: var(--border-accent) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        outline: none !important;
    }
    
    .stTextArea textarea {
        border-radius: var(--radius-md) !important;
        border: 2px solid var(--border-color) !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
        resize: none !important;
        min-height: 60px !important;
        max-height: 180px !important;
    }
    
    .stTextArea textarea:focus {
        border-color: var(--border-accent) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        outline: none !important;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: var(--radius-md) !important;
        padding: 0.65rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        border: none !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-md) !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
    }
    
    .stButton > button[kind="secondary"] {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    /* Reference Box */
    .reference-box {
        background: #fffbeb;
        border-left: 3px solid #fbbf24;
        padding: var(--spacing-sm) var(--spacing-md);
        border-radius: var(--radius-sm);
        margin: var(--spacing-sm) 0;
        font-size: 0.85rem;
        color: var(--text-secondary);
    }
    
    /* Stats Cards */
    .stats-card {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: var(--spacing-lg);
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
    }
    
    .stats-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }
    
    .stats-card h4 {
        font-size: 0.85rem;
        color: var(--text-secondary);
        margin-bottom: var(--spacing-sm);
        font-weight: 600;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: var(--bg-secondary) !important;
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--border-color) !important;
        padding: var(--spacing-sm) var(--spacing-md) !important;
        font-weight: 500 !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: var(--bg-hover) !important;
    }
    
    /* Code Blocks */
    .stCodeBlock {
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    /* Info/Warning/Error boxes */
    .stAlert {
        border-radius: var(--radius-md) !important;
        border-left-width: 4px !important;
    }
    
    /* Divider */
    hr {
        margin: var(--spacing-xl) 0 !important;
        border: none !important;
        border-top: 1px solid var(--border-light) !important;
    }
    
    /* Loading Animation */
    .loading-pulse {
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.6; }
        50% { opacity: 1; }
    }
    
    /* Animated Progress Bar */
    .animated-progress-bar {
        width: 100%;
        height: 6px;
        background: var(--border-light);
        border-radius: 3px;
        overflow: hidden;
        position: relative;
    }
    
    .progress-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, 
            var(--border-accent) 0%, 
            #60a5fa 50%, 
            var(--border-accent) 100%);
        background-size: 200% 100%;
        animation: progressSlide 1.5s ease-in-out infinite;
        border-radius: 3px;
    }
    
    @keyframes progressSlide {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    
    /* Skeleton Loading */
    .skeleton-loading {
        animation: fadeIn 0.3s ease-in;
    }
    
    .skeleton-text {
        height: 1rem;
        background: linear-gradient(90deg, 
            var(--border-light) 25%, 
            var(--border-color) 50%, 
            var(--border-light) 75%);
        background-size: 200% 100%;
        border-radius: var(--radius-sm);
        margin: 0.5rem 0;
        animation: skeletonShimmer 1.5s ease-in-out infinite;
    }
    
    @keyframes skeletonShimmer {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    
    /* Compact Mode */
    .compact-message {
        padding: var(--spacing-sm) var(--spacing-md);
        font-size: 0.85rem;
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-tertiary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }
    
    /* Context Panel */
    .context-panel {
        background: var(--bg-primary);
        border-left: 1px solid var(--border-color);
        padding: var(--spacing-lg);
        height: 100vh;
        overflow-y: auto;
    }
    
    .context-chunk {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-sm);
        padding: var(--spacing-md);
        margin-bottom: var(--spacing-md);
        font-size: 0.85rem;
    }
    
    .chunk-metadata {
        display: flex;
        gap: var(--spacing-sm);
        flex-wrap: wrap;
        margin-bottom: var(--spacing-sm);
        font-size: 0.75rem;
        color: var(--text-muted);
    }
    
    /* Welcome Screen */
    .welcome-card {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: var(--spacing-xl);
        box-shadow: var(--shadow-md);
        max-width: 800px;
        margin: var(--spacing-xl) auto;
    }
    
    /* Batch Separator */
    .message-batch-separator {
        display: flex;
        align-items: center;
        gap: var(--spacing-md);
        margin: var(--spacing-lg) 0;
        color: var(--text-muted);
        font-size: 0.8rem;
    }
    
    .message-batch-separator::before,
    .message-batch-separator::after {
        content: '';
        flex: 1;
        height: 1px;
        background: var(--border-light);
    }
    
    /* Floating Panel */
    .floating-panel {
        position: absolute;
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: var(--spacing-lg);
        box-shadow: var(--shadow-lg);
        z-index: 2000;
        min-width: 300px;
    }
    
    /* Focus Mode */
    .focus-mode .context-panel {
        display: none;
    }
    
    .focus-mode .chat-container {
        max-width: 100%;
    }
    </style>
    """
