"""
FastAPI backend for Log Analytics Assistant.
Provides REST API endpoints for the application.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn

from backend.config import get_settings
from backend.file_manager import FileManager
from backend.log_parser import LogParser
from backend.embedding_engine import EmbeddingEngine
from backend.rag_engine import RAGEngine
from backend.session_manager import SessionManager
from backend.models_registry import ModelRegistry
from backend.models import (
    CreateIssueRequest,
    UpdateKBRequest,
    QueryRequest,
    StatusResponse,
    IssueListResponse,
    ChatHistoryResponse,
    QueryResponse
)

# Initialize FastAPI app
app = FastAPI(
    title="Log Analytics Assistant API",
    description="RAG-based log analysis system with Gemini integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global component instances (initialized lazily)
_file_manager = None
_log_parser = None
_embedding_engine = None
_rag_engine = None
_session_manager = None

# Global progress tracking
_kb_build_progress = {}

# Initialize models on startup
def initialize_models():
    """Initialize and register available models based on configuration."""
    settings = get_settings()
    
    print("\n" + "="*60)
    print("🚀 Initializing AI Log Assistant")
    print("="*60)
    
    # Load Gemini models
    if settings.gemini_api_key:
        print("📦 Registering Gemini models...")
        ModelRegistry.refresh_gemini_models(settings.gemini_api_key)
    
    # Register OpenRouter models
    if settings.openrouter_api_key:
        print("📦 Registering OpenRouter models...")
        ModelRegistry.register_openrouter_models()
    
    # Register Azure OpenAI deployment
    if settings.azure_openai_deployment and settings.azure_openai_api_key and settings.azure_openai_endpoint:
        print("📦 Registering Azure OpenAI deployment...")
        print(f"   Deployment: {settings.azure_openai_deployment}")
        print(f"   Endpoint: {settings.azure_openai_endpoint}")
        print(f"   API Key: {'*' * 8}{settings.azure_openai_api_key[-4:] if len(settings.azure_openai_api_key) > 4 else '****'}")
        ModelRegistry.register_azure_model(settings.azure_openai_deployment)
    
    # Display default LLM
    print(f"\n🤖 Default LLM: {settings.llm_default}")
    print(f"📊 Available LLM models: {len(ModelRegistry.list_llm_models())}")
    
    print("="*60 + "\n")

# Initialize on module load
initialize_models()

def get_file_manager():
    """Get or create FileManager instance."""
    global _file_manager
    if _file_manager is None:
        _file_manager = FileManager()
    return _file_manager

def get_log_parser():
    """Get or create LogParser instance."""
    global _log_parser
    if _log_parser is None:
        _log_parser = LogParser()
    return _log_parser

def get_embedding_engine():
    """Get or create EmbeddingEngine instance."""
    global _embedding_engine
    if _embedding_engine is None:
        _embedding_engine = EmbeddingEngine()
    return _embedding_engine

def get_rag_engine():
    """Get or create RAGEngine instance."""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine

def get_session_manager():
    """Get or create SessionManager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Log Analytics Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "create_issue": "/create_issue",
            "list_issues": "/list_issues",
            "upload_logs": "/upload_logs/{issue_id}",
            "update_kb": "/update_kb",
            "query": "/query",
            "chat_history": "/chat_history/{issue_id}",
            "models": "/models"
        }
    }

@app.post("/create_issue", response_model=StatusResponse)
async def create_issue(request: CreateIssueRequest):
    """Create a new issue workspace."""
    try:
        issue_dir = get_file_manager().create_issue(request.issue_id)
        return StatusResponse(
            success=True,
            message=f"Issue {request.issue_id} created successfully",
            data={"issue_dir": str(issue_dir)}
        )
    except FileExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/list_issues", response_model=IssueListResponse)
async def list_issues():
    """List all issue IDs."""
    try:
        issues = get_file_manager().list_issues()
        return IssueListResponse(issues=issues)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/upload_logs/{issue_id}", response_model=StatusResponse)
async def upload_logs(issue_id: str, files: List[UploadFile] = File(...)):
    """Upload log files for an issue."""
    try:
        if not get_file_manager().issue_exists(issue_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Issue {issue_id} not found")
        
        # Read files
        file_data = []
        for file in files:
            content = await file.read()
            file_data.append((file.filename, content))
        
        # Save files
        saved_paths = get_file_manager().save_raw_logs(issue_id, file_data)
        
        return StatusResponse(
            success=True,
            message=f"Uploaded {len(saved_paths)} log files",
            data={
                "files": [p.name for p in saved_paths],
                "count": len(saved_paths)
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/update_kb", response_model=StatusResponse)
async def update_kb(request: UpdateKBRequest):
    """Update knowledge base (parse logs and build embeddings)."""
    try:
        if not get_file_manager().issue_exists(request.issue_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Issue {request.issue_id} not found")
        
        # Initialize progress
        _kb_build_progress[request.issue_id] = {
            "phase": "parsing",
            "message": "Parsing logs...",
            "percentage": 0,
            "is_building": True
        }
        
        # Parse and chunk logs
        chunks = get_log_parser().parse_and_chunk(request.issue_id)
        
        if not chunks:
            _kb_build_progress[request.issue_id] = {
                "phase": "error",
                "message": "No logs found to parse",
                "percentage": 0,
                "is_building": False
            }
            return StatusResponse(
                success=False,
                message="No logs found to parse",
                data={"chunks": 0}
            )
        
        # Progress callback for embeddings
        def progress_callback(progress_data: dict):
            _kb_build_progress[request.issue_id] = {
                **progress_data,
                "is_building": True
            }
        
        # Build embeddings with progress tracking
        get_embedding_engine().build_embeddings(
            issue_id=request.issue_id,
            embedding_model=request.embedding_model,
            force=request.force,
            progress_callback=progress_callback
        )
        
        # Mark as complete
        _kb_build_progress[request.issue_id] = {
            "phase": "complete",
            "message": f"Successfully built {len(chunks)} chunks",
            "percentage": 100,
            "is_building": False
        }
        
        return StatusResponse(
            success=True,
            message=f"Knowledge base updated with {len(chunks)} chunks",
            data={
                "chunks": len(chunks),
                "embedding_model": request.embedding_model or get_file_manager().load_metadata(request.issue_id).embedding_model
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        # Mark as error
        if request.issue_id in _kb_build_progress:
            _kb_build_progress[request.issue_id] = {
                "phase": "error",
                "message": str(e),
                "percentage": 0,
                "is_building": False
            }
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/kb_build_progress/{issue_id}")
async def get_kb_build_progress(issue_id: str):
    """Get knowledge base build progress for an issue."""
    if issue_id not in _kb_build_progress:
        return {
            "phase": "idle",
            "message": "No build in progress",
            "percentage": 0,
            "is_building": False
        }
    return _kb_build_progress[issue_id]

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Query the knowledge base."""
    try:
        if not get_file_manager().issue_exists(request.issue_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Issue {request.issue_id} not found")
        
        # Check if embeddings exist
        if not get_file_manager().get_embeddings_path(request.issue_id).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Knowledge base not built. Please run update_kb first."
            )
        
        # Save user query to history
        get_session_manager().append_chat(
            issue_id=request.issue_id,
            role="user",
            message=request.query
        )
        
        # Run RAG pipeline
        result = get_rag_engine().run_query(
            issue_id=request.issue_id,
            query=request.query,
            top_k=request.top_k,
            llm_model=request.llm_model
        )
        
        # Save assistant response to history
        get_session_manager().append_chat(
            issue_id=request.issue_id,
            role="assistant",
            message=result.answer,
            references=result.references,
            metadata=result.metadata
        )
        
        # Update metadata with last used LLM
        metadata = get_file_manager().load_metadata(request.issue_id)
        metadata.llm_model_last_used = request.llm_model or get_settings().llm_default
        get_file_manager().save_metadata(request.issue_id, metadata)
        
        return QueryResponse(
            answer=result.answer,
            references=result.references,
            context_chunks=[chunk.dict() for chunk in result.retrieved_chunks],
            metadata=result.metadata
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/chat_history/{issue_id}", response_model=ChatHistoryResponse)
async def get_chat_history(issue_id: str, limit: int = None):
    """Get chat history for an issue."""
    try:
        if not get_file_manager().issue_exists(issue_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Issue {issue_id} not found")
        
        history = get_session_manager().load_history(issue_id, limit=limit)
        
        return ChatHistoryResponse(
            issue_id=issue_id,
            history=history
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/models")
async def get_available_models():
    """Get list of available embedding and LLM models."""
    return {
        "embedding_models": ModelRegistry.list_embedding_models(),
        "llm_models": ModelRegistry.list_llm_models()
    }

@app.get("/issue_stats/{issue_id}")
async def get_issue_stats(issue_id: str):
    """Get statistics for an issue."""
    try:
        if not get_file_manager().issue_exists(issue_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Issue {issue_id} not found")
        
        metadata = get_file_manager().load_metadata(issue_id)
        chunks_count = get_log_parser().get_chunks_count(issue_id)
        conversation_summary = get_session_manager().get_conversation_summary(issue_id)
        
        return {
            "issue_id": issue_id,
            "created_at": metadata.created_at,
            "updated_at": metadata.updated_at,
            "embedding_model": metadata.embedding_model,
            "llm_model_last_used": metadata.llm_model_last_used,
            "chunks": chunks_count,
            "stats": metadata.stats,
            "conversation": conversation_summary
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def main():
    """Main entry point for the backend server."""
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
