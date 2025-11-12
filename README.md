# 🔍 Intelligent Log Analytics Assistant

A production-grade, privacy-focused RAG (Retrieval-Augmented Generation) based log analysis system that enables engineers to semantically search and interact with log files through natural language queries powered by Google Gemini API.

## ✨ Features

- **🔍 Semantic Search**: Find relevant log entries using natural language queries
- **🤖 AI-Powered Analysis**: Get insights powered by Google Gemini (1.5 Flash/Pro)
- **📊 Issue-Based Workspaces**: Organize logs by troubleshooting sessions
- **💾 Local-First Storage**: All data stored on filesystem (no external databases)
- **🔒 Privacy-Focused**: Logs never transmitted externally (only query context)
- **⚙️ Configurable Models**: Choose between embedding models (Gemini, SentenceTransformers)
- **💬 Conversational Interface**: Natural chat UI for interacting with logs
- **📈 Context-Aware**: Retrieve and display relevant log excerpts with references

## 🏗️ Architecture

```
Frontend (Streamlit)
    ↓ REST API
Backend (FastAPI)
    ↓
├─ Log Parser → Chunking
├─ Embedding Engine → Vector Generation
├─ Retriever → Similarity Search
├─ LLM Connector → Response Generation
└─ Session Manager → Chat History

Storage (Filesystem)
└─ data/issues/
    └─ ISSUE-ID/
        ├─ raw_logs/
        ├─ parsed_chunks.jsonl
        ├─ embeddings.npy
        ├─ chat_history.jsonl
        └─ metadata.json
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+** (recommended) or Python 3.10+
  - ⚠️ **Note**: Python 3.14+ may have compatibility issues on Windows. Use Python 3.13 for best results.
  - If you have both Python 3.13 and 3.14 installed, specify `--python 3.13` with UV/UVX commands
- [UV](https://docs.astral.sh/uv/) or [UVX](https://docs.astral.sh/uv/guides/tools/) (recommended)
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

#### Option 1: Using UV (Recommended)

1. **Install UV** (if not already installed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# or on Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. **Clone and setup**
```bash
git clone <repository-url>
cd AILogAssistant

# UV will automatically create venv and install dependencies
uv sync

# If you have both Python 3.13 and 3.14 (or later) installed:
# Force use of Python 3.13 for better compatibility
uv sync --python 3.13
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your API keys (GEMINI_API_KEY, AZURE_OPENAI_API_KEY, etc.)
```

4. **Run the application**
```bash
# Start backend
uv run ailog-backend

# If you have both Python 3.13 and 3.14 installed:
# Specify Python 3.13 explicitly for better compatibility
uv run --python 3.13 ailog-backend

# In another terminal, start frontend
uv run ailog-frontend
# Or with specific Python version:
uv run --python 3.13 ailog-frontend
```

#### Option 2: Using UVX (One-liner execution)

```bash
# Run backend (no installation needed!)
uvx --from ailogassistant ailog-backend

# If you have both Python 3.13 and 3.14 installed:
# Specify Python 3.13 for better compatibility
uvx --python 3.13 --from ailogassistant ailog-backend

# In another terminal, run frontend
uvx --from ailogassistant ailog-frontend
# Or with specific Python version:
uvx --python 3.13 --from ailogassistant ailog-frontend
```

**Important:** If you have Python 3.14+ installed alongside Python 3.13, always use `--python 3.13` to avoid build errors on Windows.

#### Option 3: Traditional pip install

1. **Clone repository**
```bash
git clone <repository-url>
cd AILogAssistant
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install package**
```bash
pip install -e .
# or for development
pip install -e ".[dev]"
```

4. **Configure and run**
```bash
cp .env.example .env
# Edit .env with your GEMINI_API_KEY

# Start backend
ailog-backend

# In another terminal, start frontend
ailog-frontend
```

### Quick Test Drive

**Run both frontend and backend together:**

```bash
# Using UV - Method 1: Background process
uv run ailog-backend &
uv run ailog-frontend

# Using UV - Method 2: Separate terminals
# Terminal 1:
uv run ailog-backend

# Terminal 2 (new terminal):
uv run ailog-frontend

# If you have both Python 3.13 and 3.14 installed:
# Terminal 1:
uv run --python 3.13 ailog-backend

# Terminal 2:
uv run --python 3.13 ailog-frontend
```

**Using UVX (no installation):**
```bash
# Terminal 1:
uvx --python 3.13 --from ailogassistant ailog-backend

# Terminal 2 (new terminal):
uvx --python 3.13 --from ailogassistant ailog-frontend
```

**Access the application:**
- Backend API: `http://localhost:8000`
- Frontend UI: `http://localhost:8501`
- API Documentation: `http://localhost:8000/docs`

## 📖 Usage Guide

### 1. Create an Issue
- Use the sidebar to create a new issue workspace (e.g., `ISSUE-2024-001`)
- Or select an existing issue

### 2. Upload Logs
- Upload one or more log files (.log, .txt, .jsonl)
- Supported formats: plain text, JSON lines

### 3. Configure Models (Optional)
- **Embedding Model**: Choose between Gemini (cloud) or local models
  - `gemini:text-embedding-004` - Cloud, 768 dimensions
  - `st:all-MiniLM-L6-v2` - Local, fast, 384 dimensions
  - `st:all-mpnet-base-v2` - Local, accurate, 768 dimensions
  
- **LLM Model**: Select response generation model
  - `gemini-1.5-flash` - Fast responses
  - `gemini-1.5-pro` - More accurate analysis

### 4. Build Knowledge Base
- Click "Build/Update KB" to parse logs and generate embeddings
- This creates searchable vector representations of your logs
- Check "Force Rebuild" to regenerate embeddings with a different model

### 5. Ask Questions
- Type natural language questions about your logs
- Examples:
  - "What errors occurred in the application?"
  - "Show me all database timeout issues"
  - "What happened around 10:45?"
  - "Why did the payment processing fail?"

### 6. Review Responses
- AI generates answers based on relevant log excerpts
- Click "References" to see which log files were used
- View context chunks to inspect the actual log entries

## 🎯 Example Queries

```
"What caused the application to crash?"
"Show me all database connection errors"
"What warnings were logged between 10:30 and 11:00?"
"Explain the NullPointerException"
"What was the response time for API requests?"
"Why was the IP address blocked?"
"What happened before the Redis connection was lost?"
```

## 📁 Project Structure

```
AILogAssistant/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── models.py               # Pydantic schemas
│   ├── file_manager.py         # File operations
│   ├── log_parser.py           # Log chunking
│   ├── embedding_engine.py     # Embedding generation
│   ├── models_registry.py      # Model strategies
│   ├── retriever.py            # Similarity search
│   ├── llm_connector.py        # LLM API integration
│   ├── rag_engine.py           # RAG orchestration
│   ├── session_manager.py      # Chat history
│   └── utils.py                # Helper functions
├── frontend/
│   ├── app.py                  # Main Streamlit app
│   └── components/
│       ├── sidebar.py          # Sidebar UI
│       ├── chat_ui.py          # Chat interface
│       └── context_viewer.py   # Context display
├── data/
│   ├── config.yaml             # Runtime configuration
│   └── issues/                 # Issue workspaces
├── sample_logs/
│   └── application.log         # Sample log file
├── tests/                      # Test files
├── .env.example                # Environment template
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here  # Optional

# Configuration
ROOT_DIRECTORY=./data
```

### Using OpenRouter (Alternative/Additional LLM Provider)

The system now supports OpenRouter alongside Gemini, giving you access to multiple LLM providers including OpenAI, Anthropic, Meta Llama, and more through a single API.

**Setup:**
1. Get an OpenRouter API key from [openrouter.ai](https://openrouter.ai/)
2. Add to your `.env` file:
   ```bash
   OPENROUTER_API_KEY=sk-or-v1-...
   ```

**Available Models:**
- `openrouter:openai/gpt-4o-mini` - Fast, cost-effective
- `openrouter:openai/gpt-4o` - Most capable OpenAI model
- `openrouter:anthropic/claude-3.5-sonnet` - Excellent reasoning
- `openrouter:anthropic/claude-3-haiku` - Fast, affordable
- `openrouter:meta-llama/llama-3.1-8b-instruct` - Open source
- `openrouter:meta-llama/llama-3.1-70b-instruct` - Larger Llama
- `openrouter:google/gemini-pro-1.5` - Gemini via OpenRouter
- `openrouter:mistralai/mistral-7b-instruct` - Mistral AI
- And many more...

**Usage:**
- Select an OpenRouter model from the dropdown in the UI
- Or specify in config.yaml: `llm_default: "openrouter:openai/gpt-4o-mini"`
- The system will automatically use the appropriate API key

**Benefits:**
- Access to multiple providers without separate integrations
- Pay-as-you-go pricing
- Automatic fallback between providers
- Cost tracking and analytics via OpenRouter dashboard

### Using Azure OpenAI

Azure OpenAI provides enterprise-grade access to OpenAI models with additional security, compliance, and regional deployment options.

**Setup:**
1. Create an Azure OpenAI resource in the Azure Portal
2. Deploy a model (e.g., GPT-4, GPT-3.5-turbo) to get a deployment name
3. Get your API key and endpoint from Azure Portal
4. Add to your `.env` file:
   ```bash
   AZURE_OPENAI_API_KEY=your_azure_api_key
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT=your-deployment-name
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   ```

**Configuration:**
- **API Key**: Found in Azure Portal → Your OpenAI Resource → Keys and Endpoint
- **Endpoint**: Your resource's endpoint URL (ends with `openai.azure.com/`)
- **Deployment**: The name you gave your model deployment
- **API Version**: Azure API version (default: `2024-02-15-preview`)

**Usage:**
- Model naming: `azure:<deployment-name>`
- Example: If your deployment is named `gpt-4-deployment`, use `azure:gpt-4-deployment`
- Select from UI dropdown or set in config.yaml: `llm_default: "azure:gpt-4-deployment"`

**Benefits:**
- Enterprise security and compliance
- Private networking options
- Regional data residency
- SLA guarantees
- Integration with Azure services
- Unified billing with other Azure resources

### Runtime Configuration (data/config.yaml)
```yaml
chunk_size: 800          # Characters per chunk
overlap: 100             # Overlap between chunks
top_k: 5                 # Chunks to retrieve
embedding_default: "gemini:text-embedding-004"
llm_default: "gemini-1.5-flash"
llm_temperature: 0.1
llm_max_tokens: 2048
log_extensions: [".log", ".txt", ".jsonl"]
```

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/create_issue` | POST | Create new issue workspace |
| `/list_issues` | GET | List all issues |
| `/upload_logs/{issue_id}` | POST | Upload log files |
| `/update_kb` | POST | Build/update knowledge base |
| `/query` | POST | Query logs |
| `/chat_history/{issue_id}` | GET | Get chat history |
| `/models` | GET | List available models |
| `/issue_stats/{issue_id}` | GET | Get issue statistics |

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

## 🔐 Security & Privacy

- ✅ All logs stored locally on your filesystem
- ✅ No external database dependencies
- ✅ Only query text and retrieved context sent to Gemini API
- ✅ API keys stored in .env (not committed to git)
- ✅ Full control over data retention

## 📊 Performance Considerations

- **Batch Processing**: Embeddings generated in configurable batches
- **Caching**: Text hash-based caching to avoid re-embedding
- **Memory Mapping**: Efficient loading of large embedding arrays
- **Chunking Strategy**: Line-based chunking with overlap for context preservation

## 🛠️ Troubleshooting

### UV Installation Issues (Windows/Python 3.14+)

If you encounter build errors with `uv run` due to missing compilers (cmake, zlib, etc.):

**Solution 1: Use Python 3.13 with UV** (Recommended)
```bash
# Install/sync with Python 3.13
uv sync --python 3.13

# Run with Python 3.13
uv run --python 3.13 ailog-backend
```

**Solution 2: Use pip instead**
```bash
# Create virtual environment with Python 3.13
python3.13 -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install with pip
pip install -e .

# Run using the startup script
python start_backend.py

# Or run directly
ailog-backend
```

**Why this happens**: UV tries to build packages from source for newer Python versions (3.14+) that don't have prebuilt wheels yet. Python 3.13 has better package support with prebuilt wheels available.

**Finding your Python version:**
```bash
# List available Python versions
uv python list

# Check current Python version
python --version
python3.13 --version  # Specific version
```

### "GEMINI_API_KEY not found"
- Ensure `.env` file exists in project root
- Verify API key is set: `GEMINI_API_KEY=your_key`

### "Knowledge base not built"
- Upload logs first
- Click "Build/Update KB" button
- Check console for errors

### Slow embedding generation
- Reduce `chunk_size` in config.yaml
- Use local embedding model (MiniLM) instead of Gemini
- Reduce `embedding_batch_size`

### High memory usage
- Reduce number of chunks (increase `chunk_size`)
- Use memory-mapped embeddings (already default)
- Clear old issue workspaces

## 🚧 Future Enhancements

- [ ] Log correlation heatmap visualization
- [ ] JIRA integration for issue tracking
- [ ] Multi-user support with authentication
- [ ] Real-time log streaming
- [ ] Advanced filtering and faceted search
- [ ] Export analysis reports
- [ ] Custom embedding models
- [ ] Kubernetes deployment configs

## 📝 License

This project is provided as-is for educational and internal use.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

For issues and questions:
- Create an issue in the repository
- Check existing documentation
- Review API documentation at `http://localhost:8000/docs`

## 🙏 Acknowledgments

- Google Gemini API for LLM capabilities
- Sentence Transformers for local embeddings
- FastAPI and Streamlit for excellent frameworks

---

**Built with ❤️ for engineers analyzing logs**
