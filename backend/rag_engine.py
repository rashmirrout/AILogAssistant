"""
RAG (Retrieval-Augmented Generation) engine.
Orchestrates the complete RAG pipeline: retrieve → generate.
"""

from typing import Optional
from datetime import datetime
from backend.config import get_settings
from backend.retriever import Retriever
from backend.llm_connector import LLMConnector
from backend.models import RAGResult

class RAGEngine:
    """Orchestrates the RAG pipeline."""
    
    def __init__(self):
        self.settings = get_settings()
        self.retriever = Retriever()
        self.llm_connector = LLMConnector()
    
    def run_query(
        self,
        issue_id: str,
        query: str,
        top_k: Optional[int] = None,
        llm_model: Optional[str] = None
    ) -> RAGResult:
        """
        Run the complete RAG pipeline for a query.
        
        Pipeline steps:
        1. Retrieve top-k relevant chunks
        2. Generate response using LLM with context
        3. Return structured result
        
        Args:
            issue_id: Issue ID to query
            query: User's question
            top_k: Number of chunks to retrieve (defaults to config)
            llm_model: LLM model to use (defaults to config)
            
        Returns:
            RAGResult with answer, references, and chunks
        """
        # Use default top_k if not specified
        k = top_k or self.settings.top_k
        
        # Step 1: Retrieve relevant chunks
        print(f"Retrieving top {k} chunks for query: {query[:50]}...")
        retrieved_chunks = self.retriever.retrieve(
            issue_id=issue_id,
            query=query,
            top_k=k
        )
        
        if not retrieved_chunks:
            return RAGResult(
                answer="No relevant log data found for this query.",
                references=[],
                retrieved_chunks=[],
                metadata={
                    "query": query,
                    "top_k": k,
                    "timestamp": datetime.now().isoformat(),
                    "chunks_found": 0
                }
            )
        
        print(f"Retrieved {len(retrieved_chunks)} chunks")
        
        # Step 2: Generate response using LLM
        print("Generating response...")
        llm_response = self.llm_connector.generate_response(
            context_chunks=retrieved_chunks,
            user_query=query,
            llm_model=llm_model
        )
        
        # Step 3: Construct result
        result = RAGResult(
            answer=llm_response["answer"],
            references=llm_response["references"],
            retrieved_chunks=retrieved_chunks,
            metadata={
                "query": query,
                "top_k": k,
                "timestamp": datetime.now().isoformat(),
                "chunks_retrieved": len(retrieved_chunks),
                "llm_model": llm_model or self.settings.llm_default,
                "fallback": llm_response.get("fallback", False)
            }
        )
        
        print("Response generated successfully")
        return result
