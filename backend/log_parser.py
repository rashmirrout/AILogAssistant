"""
Log parser module for chunking and normalizing log files.
"""

import json
from pathlib import Path
from typing import List
from backend.config import get_settings
from backend.file_manager import FileManager
from backend.models import Chunk
from backend.utils import TimestampNormalizer, chunk_by_lines, deduplicate_lines, compute_text_hash

class LogParser:
    """Parse and chunk log files."""
    
    def __init__(self):
        self.settings = get_settings()
        self.file_manager = FileManager()
    
    def parse_and_chunk(self, issue_id: str) -> List[Chunk]:
        """
        Parse all log files for an issue and create chunks.
        
        Args:
            issue_id: Issue ID to parse logs for
            
        Returns:
            List of parsed chunks
        """
        log_files = self.file_manager.get_raw_log_files(issue_id)
        
        if not log_files:
            return []
        
        all_chunks = []
        chunk_counter = 0
        
        for log_file in log_files:
            chunks = self._parse_file(issue_id, log_file, chunk_counter)
            all_chunks.extend(chunks)
            chunk_counter += len(chunks)
        
        # Save chunks to JSONL file
        self._save_chunks(issue_id, all_chunks)
        
        return all_chunks
    
    def _parse_file(self, issue_id: str, file_path: Path, start_chunk_id: int) -> List[Chunk]:
        """
        Parse a single log file and create chunks.
        
        Args:
            issue_id: Issue ID
            file_path: Path to log file
            start_chunk_id: Starting chunk ID number
            
        Returns:
            List of chunks from this file
        """
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []
        
        # Remove duplicate lines while preserving order
        unique_lines = deduplicate_lines(lines)
        
        # Estimate lines per chunk based on chunk_size
        # Assuming average line length of 100 characters
        avg_line_length = 100
        lines_per_chunk = max(1, self.settings.chunk_size // avg_line_length)
        overlap_lines = max(0, self.settings.overlap // avg_line_length)
        
        # Create line-based chunks
        line_chunks = chunk_by_lines(unique_lines, lines_per_chunk, overlap_lines)
        
        chunks = []
        for idx, (chunk_lines, start_line, end_line) in enumerate(line_chunks):
            chunk_text = ''.join(chunk_lines)
            
            # Skip empty chunks
            if not chunk_text.strip():
                continue
            
            # Extract timestamp range
            timestamp_range = TimestampNormalizer.get_timestamp_range(chunk_text)
            
            # Create chunk object
            chunk = Chunk(
                chunk_id=f"{issue_id}_chunk_{start_chunk_id + idx}",
                issue_id=issue_id,
                source_file=file_path.name,
                start_line=start_line,
                end_line=end_line,
                text=chunk_text.strip(),
                timestamp_range=list(timestamp_range) if timestamp_range else None,
                metadata={
                    "file_path": str(file_path),
                    "text_hash": compute_text_hash(chunk_text.strip())
                }
            )
            
            chunks.append(chunk)
        
        return chunks
    
    def _save_chunks(self, issue_id: str, chunks: List[Chunk]):
        """
        Save chunks to JSONL file.
        
        Args:
            issue_id: Issue ID
            chunks: List of chunks to save
        """
        chunks_path = self.file_manager.get_chunks_path(issue_id)
        
        with open(chunks_path, 'w', encoding='utf-8') as f:
            for chunk in chunks:
                f.write(chunk.json() + '\n')
    
    def load_chunks(self, issue_id: str) -> List[Chunk]:
        """
        Load chunks from JSONL file.
        
        Args:
            issue_id: Issue ID
            
        Returns:
            List of chunks
        """
        chunks_path = self.file_manager.get_chunks_path(issue_id)
        
        if not chunks_path.exists():
            return []
        
        chunks = []
        with open(chunks_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    chunk_data = json.loads(line)
                    chunks.append(Chunk(**chunk_data))
        
        return chunks
    
    def get_chunk_by_id(self, issue_id: str, chunk_id: str) -> Chunk:
        """
        Get a specific chunk by ID.
        
        Args:
            issue_id: Issue ID
            chunk_id: Chunk ID
            
        Returns:
            Chunk object
            
        Raises:
            ValueError: If chunk not found
        """
        chunks = self.load_chunks(issue_id)
        
        for chunk in chunks:
            if chunk.chunk_id == chunk_id:
                return chunk
        
        raise ValueError(f"Chunk {chunk_id} not found")
    
    def get_chunks_count(self, issue_id: str) -> int:
        """
        Get the number of chunks for an issue.
        
        Args:
            issue_id: Issue ID
            
        Returns:
            Number of chunks
        """
        chunks_path = self.file_manager.get_chunks_path(issue_id)
        
        if not chunks_path.exists():
            return 0
        
        count = 0
        with open(chunks_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    count += 1
        
        return count
