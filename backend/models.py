"""
Pydantic models for request/response schemas and data structures.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# Request Models

class CreateIssueRequest(BaseModel):
    """Request to create a new issue workspace."""
    issue_id: str = Field(..., description="Unique identifier for the issue")


class UpdateKBRequest(BaseModel):
    """Request to update knowledge base for an issue."""
    issue_id: str = Field(..., description="Issue ID to update")
    embedding_model: Optional[str] = Field(None, description="Embedding model to use")
    force: bool = Field(False, description="Force rebuild even if embeddings exist")


class QueryRequest(BaseModel):
    """Request to query the knowledge base."""
    issue_id: str = Field(..., description="Issue ID to query")
    query: str = Field(..., description="User's question")
    top_k: Optional[int] = Field(None, description="Number of chunks to retrieve")
    llm_model: Optional[str] = Field(None, description="LLM model to use for generation")


# Response Models

class StatusResponse(BaseModel):
    """Generic status response."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class IssueListResponse(BaseModel):
    """Response containing list of issues."""
    issues: List[str]


class ChatMessage(BaseModel):
    """Chat message structure."""
    timestamp: str
    role: str  # "user" or "assistant"
    message: str
    references: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatHistoryResponse(BaseModel):
    """Response containing chat history."""
    issue_id: str
    history: List[ChatMessage]


class QueryResponse(BaseModel):
    """Response to a query."""
    answer: str
    references: List[str]
    context_chunks: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


# Data Models

class Chunk(BaseModel):
    """Represents a parsed log chunk."""
    chunk_id: str
    issue_id: str
    source_file: str
    start_line: int
    end_line: int
    text: str
    timestamp_range: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        """Pydantic config."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class IssueMetadata(BaseModel):
    """Metadata for an issue workspace."""
    issue_id: str
    created_at: str
    updated_at: str
    embedding_model: str
    llm_model_last_used: Optional[str] = None
    stats: Dict[str, Any] = Field(default_factory=dict)
    models_history: List[Dict[str, str]] = Field(default_factory=list)


class RAGResult(BaseModel):
    """Result from RAG pipeline."""
    answer: str
    references: List[str]
    retrieved_chunks: List[Chunk]
    metadata: Dict[str, Any] = Field(default_factory=dict)
