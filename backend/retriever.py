"""
Retriever module for finding relevant chunks using cosine similarity.
"""

import numpy as np
from typing import List, Tuple
from backend.file_manager import FileManager
from backend.log_parser import LogParser
from backend.embedding_engine import EmbeddingEngine
from backend.models import Chunk

class Retriever:
    """Retrieve relevant chunks using semantic similarity."""
    
    def __init__(self):
        self.file_manager = FileManager()
        self.log_parser = LogParser()
        self.embedding_engine = EmbeddingEngine()
    
    def retrieve(self, issue_id: str, query: str, top_k: int = 5, embedding_model: str = None) -> List[Chunk]:
        """
        Retrieve top-k most relevant chunks for a query.
        
        Args:
            issue_id: Issue ID
            query: Query text
            top_k: Number of chunks to retrieve
            embedding_model: Model used for embeddings (must match stored embeddings)
            
        Returns:
            List of top-k relevant chunks, ordered by relevance
        """
        # Load chunks and embeddings
        chunks = self.log_parser.load_chunks(issue_id)
        
        if not chunks:
            raise ValueError(f"No chunks found for issue {issue_id}")
        
        chunk_embeddings = self.embedding_engine.load_embeddings(issue_id)
        
        # Get metadata to determine which embedding model was used
        metadata = self.file_manager.load_metadata(issue_id)
        stored_model = metadata.embedding_model
        
        # Generate query embedding using the same model as stored embeddings
        query_embedding = self.embedding_engine.get_query_embedding(query, stored_model)
        
        # Compute similarities
        similarities = self._compute_cosine_similarity(chunk_embeddings, query_embedding)
        
        # Get top-k indices
        top_k = min(top_k, len(chunks))
        top_indices = self._get_top_k_indices(similarities, top_k)
        
        # Return top chunks
        return [chunks[idx] for idx in top_indices]
    
    def _compute_cosine_similarity(self, embeddings: np.ndarray, query_embedding: np.ndarray) -> np.ndarray:
        """
        Compute cosine similarity between query and all embeddings.
        
        Args:
            embeddings: Array of shape (n_chunks, embedding_dim)
            query_embedding: Array of shape (embedding_dim,)
            
        Returns:
            Array of similarities of shape (n_chunks,)
        """
        # Normalize embeddings
        embeddings_norm = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-8)
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)
        
        # Compute dot product (cosine similarity for normalized vectors)
        similarities = np.dot(embeddings_norm, query_norm)
        
        return similarities
    
    def _get_top_k_indices(self, similarities: np.ndarray, k: int) -> List[int]:
        """
        Get indices of top-k highest similarities.
        
        Args:
            similarities: Array of similarity scores
            k: Number of top items to retrieve
            
        Returns:
            List of indices sorted by similarity (highest first)
        """
        # Use argpartition for efficiency with large arrays
        if k >= len(similarities):
            # If k >= array length, just sort all
            return np.argsort(similarities)[::-1].tolist()
        
        # Get indices of k largest elements (not sorted)
        partition_indices = np.argpartition(similarities, -k)[-k:]
        
        # Sort these k indices by their similarity values
        top_k_sorted = partition_indices[np.argsort(similarities[partition_indices])[::-1]]
        
        return top_k_sorted.tolist()
    
    def get_similarities(self, issue_id: str, query: str) -> List[Tuple[Chunk, float]]:
        """
        Get all chunks with their similarity scores.
        
        Args:
            issue_id: Issue ID
            query: Query text
            
        Returns:
            List of (chunk, similarity) tuples sorted by similarity
        """
        chunks = self.log_parser.load_chunks(issue_id)
        chunk_embeddings = self.embedding_engine.load_embeddings(issue_id)
        
        # Get metadata to determine embedding model
        metadata = self.file_manager.load_metadata(issue_id)
        query_embedding = self.embedding_engine.get_query_embedding(query, metadata.embedding_model)
        
        similarities = self._compute_cosine_similarity(chunk_embeddings, query_embedding)
        
        # Create list of (chunk, similarity) tuples
        chunk_sim_pairs = list(zip(chunks, similarities.tolist()))
        
        # Sort by similarity (highest first)
        chunk_sim_pairs.sort(key=lambda x: x[1], reverse=True)
        
        return chunk_sim_pairs
