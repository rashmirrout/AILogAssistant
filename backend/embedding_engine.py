"""
Embedding engine for generating and managing embeddings.
Supports caching and batch processing.
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Callable
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
from backend.config import get_settings
from backend.file_manager import FileManager
from backend.log_parser import LogParser
from backend.models_registry import ModelRegistry
from backend.utils import compute_text_hash, batch_items

class EmbeddingEngine:
    """Manages embedding generation and caching."""
    
    def __init__(self):
        self.settings = get_settings()
        self.file_manager = FileManager()
        self.log_parser = LogParser()
    
    def build_embeddings(self, issue_id: str, embedding_model: Optional[str] = None, force: bool = False, progress_callback: Optional[Callable[[dict], None]] = None):
        """
        Build embeddings for all chunks in an issue.
        
        Args:
            issue_id: Issue ID
            embedding_model: Model to use (defaults to config setting)
            force: Force rebuild even if embeddings exist
            progress_callback: Optional callback function for progress updates
        """
        if not self.file_manager.issue_exists(issue_id):
            raise FileNotFoundError(f"Issue {issue_id} does not exist")
        
        # Load metadata
        metadata = self.file_manager.load_metadata(issue_id)
        
        # Determine embedding model to use
        model_name = embedding_model or metadata.embedding_model
        
        # Check if rebuild is needed
        embeddings_path = self.file_manager.get_embeddings_path(issue_id)
        
        if embeddings_path.exists() and not force and metadata.embedding_model == model_name:
            print(f"Embeddings already exist for {issue_id} with model {model_name}")
            return
        
        # If model changed, we need to rebuild
        if metadata.embedding_model != model_name:
            print(f"Embedding model changed from {metadata.embedding_model} to {model_name}, rebuilding...")
            force = True
        
        # Progress: Loading chunks
        if progress_callback:
            progress_callback({
                "phase": "loading",
                "message": "Loading chunks...",
                "percentage": 5
            })
        
        # Load chunks
        chunks = self.log_parser.load_chunks(issue_id)
        
        if not chunks:
            raise ValueError(f"No chunks found for issue {issue_id}. Run parse_and_chunk first.")
        
        # Get embedding strategy
        strategy = ModelRegistry.get_embedding_strategy(model_name, self.settings.gemini_api_key)
        
        # Progress: Checking cache
        if progress_callback:
            progress_callback({
                "phase": "cache",
                "message": "Checking cache...",
                "percentage": 10
            })
        
        # Load cache if not forcing rebuild
        cache = {}
        if not force and self.settings.enable_embedding_cache:
            cache = self._load_cache(issue_id)
        
        # Prepare texts to embed
        texts_to_embed = []
        chunk_indices = []
        embeddings_list = []
        
        for idx, chunk in enumerate(chunks):
            text_hash = chunk.metadata.get("text_hash") or compute_text_hash(chunk.text)
            
            # Check cache
            if text_hash in cache and not force:
                embeddings_list.append(cache[text_hash])
            else:
                texts_to_embed.append(chunk.text)
                chunk_indices.append(idx)
        
        # Generate new embeddings in batches
        if texts_to_embed:
            print(f"Generating embeddings for {len(texts_to_embed)} chunks...")
            
            batches = batch_items(texts_to_embed, self.settings.embedding_batch_size)
            new_embeddings = []
            
            for batch_idx, batch in enumerate(batches):
                # Progress update for each batch
                batch_progress = 15 + int((batch_idx / len(batches)) * 70)  # 15-85%
                if progress_callback:
                    progress_callback({
                        "phase": "embedding",
                        "message": f"Generating embeddings (batch {batch_idx + 1}/{len(batches)})...",
                        "percentage": batch_progress,
                        "current_batch": batch_idx + 1,
                        "total_batches": len(batches)
                    })
                
                print(f"Processing batch {batch_idx + 1}/{len(batches)}")
                batch_embeddings = strategy.embed_texts(batch)
                new_embeddings.extend(batch_embeddings)
            
            # Update cache
            for idx, text_idx in enumerate(chunk_indices):
                chunk = chunks[text_idx]
                text_hash = chunk.metadata.get("text_hash") or compute_text_hash(chunk.text)
                cache[text_hash] = new_embeddings[idx].tolist()
        
        # Progress: Finalizing
        if progress_callback:
            progress_callback({
                "phase": "finalizing",
                "message": "Finalizing embeddings...",
                "percentage": 90
            })
        
        # Reconstruct full embeddings array in correct order
        final_embeddings = []
        new_embedding_idx = 0
        
        for idx, chunk in enumerate(chunks):
            text_hash = chunk.metadata.get("text_hash") or compute_text_hash(chunk.text)
            
            if text_hash in cache:
                final_embeddings.append(cache[text_hash])
            else:
                final_embeddings.append(new_embeddings[new_embedding_idx].tolist())
                new_embedding_idx += 1
        
        # Convert to numpy array
        embeddings_array = np.array(final_embeddings, dtype=np.float32)
        
        # Save embeddings
        np.save(embeddings_path, embeddings_array)
        
        # Save cache
        if self.settings.enable_embedding_cache:
            self._save_cache(issue_id, cache)
        
        # Update metadata
        metadata.embedding_model = model_name
        metadata.updated_at = datetime.now().isoformat()
        metadata.stats["num_chunks"] = len(chunks)
        metadata.stats["embedding_dim"] = strategy.get_embedding_dim()
        
        # Add to models history
        metadata.models_history.append({
            "timestamp": datetime.now().isoformat(),
            "embedding_model": model_name
        })
        
        self.file_manager.save_metadata(issue_id, metadata)
        
        # Progress: Complete
        if progress_callback:
            progress_callback({
                "phase": "complete",
                "message": f"Successfully built {len(chunks)} chunks",
                "percentage": 100
            })
        
        print(f"Successfully built embeddings for {len(chunks)} chunks")
    
    def load_embeddings(self, issue_id: str) -> np.ndarray:
        """
        Load embeddings for an issue.
        
        Args:
            issue_id: Issue ID
            
        Returns:
            NumPy array of embeddings
        """
        embeddings_path = self.file_manager.get_embeddings_path(issue_id)
        
        if not embeddings_path.exists():
            raise FileNotFoundError(f"Embeddings not found for issue {issue_id}. Run build_embeddings first.")
        
        # Use memory mapping for efficiency
        return np.load(embeddings_path, mmap_mode='r')
    
    def get_query_embedding(self, query: str, embedding_model: Optional[str] = None) -> np.ndarray:
        """
        Generate embedding for a query.
        
        Args:
            query: Query text
            embedding_model: Model to use (defaults to config setting)
            
        Returns:
            Query embedding vector
        """
        model_name = embedding_model or self.settings.embedding_default
        strategy = ModelRegistry.get_embedding_strategy(model_name, self.settings.gemini_api_key)
        
        embeddings = strategy.embed_texts([query])
        return embeddings[0]
    
    def _load_cache(self, issue_id: str) -> Dict[str, list]:
        """Load embedding cache from file."""
        cache_path = self.file_manager.get_cache_path(issue_id)
        
        if not cache_path.exists():
            return {}
        
        try:
            with open(cache_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def _save_cache(self, issue_id: str, cache: Dict[str, list]):
        """Save embedding cache to file."""
        cache_path = self.file_manager.get_cache_path(issue_id)
        
        # Limit cache size
        if len(cache) > self.settings.max_chunk_cache_size:
            # Keep only most recent entries (simple FIFO)
            cache_items = list(cache.items())
            cache = dict(cache_items[-self.settings.max_chunk_cache_size:])
        
        with open(cache_path, 'w') as f:
            json.dump(cache, f)
