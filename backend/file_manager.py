"""
File management utilities for issue workspaces.
Handles directory creation, file operations, and path management.
"""

import json
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from backend.config import get_settings
from backend.models import IssueMetadata

class FileManager:
    """Manages file operations for issue workspaces."""
    
    def __init__(self):
        self.settings = get_settings()
        self.issues_root = self.settings.root_directory / "issues"
        self.issues_root.mkdir(parents=True, exist_ok=True)
    
    def get_issue_dir(self, issue_id: str) -> Path:
        """Get the directory path for an issue."""
        return self.issues_root / issue_id
    
    def get_raw_logs_dir(self, issue_id: str) -> Path:
        """Get the raw logs directory for an issue."""
        return self.get_issue_dir(issue_id) / "raw_logs"
    
    def get_chunks_path(self, issue_id: str) -> Path:
        """Get the path to parsed chunks file."""
        return self.get_issue_dir(issue_id) / "parsed_chunks.jsonl"
    
    def get_embeddings_path(self, issue_id: str) -> Path:
        """Get the path to embeddings file."""
        return self.get_issue_dir(issue_id) / "embeddings.npy"
    
    def get_metadata_path(self, issue_id: str) -> Path:
        """Get the path to metadata file."""
        return self.get_issue_dir(issue_id) / "metadata.json"
    
    def get_chat_history_path(self, issue_id: str) -> Path:
        """Get the path to chat history file."""
        return self.get_issue_dir(issue_id) / "chat_history.jsonl"
    
    def get_cache_path(self, issue_id: str) -> Path:
        """Get the path to embedding cache file."""
        return self.get_issue_dir(issue_id) / "embedding_cache.json"
    
    def create_issue(self, issue_id: str) -> Path:
        """
        Create a new issue workspace.
        
        Args:
            issue_id: Unique identifier for the issue
            
        Returns:
            Path to the created issue directory
            
        Raises:
            FileExistsError: If issue already exists
        """
        issue_dir = self.get_issue_dir(issue_id)
        
        if issue_dir.exists():
            raise FileExistsError(f"Issue {issue_id} already exists")
        
        # Create directory structure
        issue_dir.mkdir(parents=True)
        raw_logs_dir = self.get_raw_logs_dir(issue_id)
        raw_logs_dir.mkdir()
        
        # Create metadata
        metadata = IssueMetadata(
            issue_id=issue_id,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            embedding_model=self.settings.embedding_default,
            stats={}
        )
        
        self.save_metadata(issue_id, metadata)
        
        # Initialize empty chat history
        chat_history_path = self.get_chat_history_path(issue_id)
        chat_history_path.touch()
        
        return issue_dir
    
    def list_issues(self) -> List[str]:
        """
        List all issue IDs.
        
        Returns:
            List of issue IDs
        """
        if not self.issues_root.exists():
            return []
        
        return [d.name for d in self.issues_root.iterdir() if d.is_dir()]
    
    def issue_exists(self, issue_id: str) -> bool:
        """Check if an issue exists."""
        return self.get_issue_dir(issue_id).exists()
    
    def save_raw_logs(self, issue_id: str, files: List[tuple]) -> List[Path]:
        """
        Save uploaded log files to raw_logs directory.
        
        Args:
            issue_id: Issue ID
            files: List of (filename, content) tuples
            
        Returns:
            List of saved file paths
        """
        if not self.issue_exists(issue_id):
            raise FileNotFoundError(f"Issue {issue_id} does not exist")
        
        raw_logs_dir = self.get_raw_logs_dir(issue_id)
        saved_paths = []
        
        for filename, content in files:
            file_path = raw_logs_dir / filename
            
            # Handle binary vs text content
            if isinstance(content, bytes):
                file_path.write_bytes(content)
            else:
                file_path.write_text(content, encoding='utf-8')
            
            saved_paths.append(file_path)
        
        # Update metadata
        metadata = self.load_metadata(issue_id)
        metadata.updated_at = datetime.now().isoformat()
        self.save_metadata(issue_id, metadata)
        
        return saved_paths
    
    def get_raw_log_files(self, issue_id: str) -> List[Path]:
        """
        Get list of raw log files for an issue.
        
        Args:
            issue_id: Issue ID
            
        Returns:
            List of log file paths
        """
        if not self.issue_exists(issue_id):
            raise FileNotFoundError(f"Issue {issue_id} does not exist")
        
        raw_logs_dir = self.get_raw_logs_dir(issue_id)
        
        if not raw_logs_dir.exists():
            return []
        
        # Filter by allowed extensions
        log_files = []
        for ext in self.settings.log_extensions:
            log_files.extend(raw_logs_dir.glob(f"*{ext}"))
        
        return sorted(log_files)
    
    def save_metadata(self, issue_id: str, metadata: IssueMetadata):
        """Save metadata to file."""
        metadata_path = self.get_metadata_path(issue_id)
        with open(metadata_path, 'w') as f:
            json.dump(metadata.dict(), f, indent=2)
    
    def load_metadata(self, issue_id: str) -> IssueMetadata:
        """Load metadata from file."""
        metadata_path = self.get_metadata_path(issue_id)
        
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata not found for issue {issue_id}")
        
        with open(metadata_path, 'r') as f:
            data = json.load(f)
        
        return IssueMetadata(**data)
    
    def delete_issue(self, issue_id: str):
        """Delete an issue workspace and all its data."""
        issue_dir = self.get_issue_dir(issue_id)
        
        if issue_dir.exists():
            shutil.rmtree(issue_dir)
