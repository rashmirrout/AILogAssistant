"""
Utility functions for log processing and text operations.
"""

import re
import hashlib
from typing import List, Optional, Tuple
from datetime import datetime

class TimestampNormalizer:
    """Normalize various timestamp formats to ISO 8601."""
    
    # Common timestamp patterns
    PATTERNS = [
        # ISO 8601: 2024-01-15T10:30:45.123Z
        (r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?', 
         lambda m: m.group(0)),
        
        # YYYY-MM-DD HH:MM:SS
        (r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(?:\.\d+)?',
         lambda m: m.group(0).replace(' ', 'T')),
        
        # DD/MMM/YYYY:HH:MM:SS (Apache/nginx)
        (r'\d{2}/[A-Za-z]{3}/\d{4}:\d{2}:\d{2}:\d{2}',
         lambda m: datetime.strptime(m.group(0), '%d/%b/%Y:%H:%M:%S').isoformat()),
        
        # Unix timestamp (10 digits)
        (r'\b\d{10}\b',
         lambda m: datetime.fromtimestamp(int(m.group(0))).isoformat()),
        
        # Unix timestamp milliseconds (13 digits)
        (r'\b\d{13}\b',
         lambda m: datetime.fromtimestamp(int(m.group(0)) / 1000).isoformat()),
    ]
    
    @classmethod
    def extract_timestamps(cls, text: str) -> List[str]:
        """
        Extract all timestamps from text.
        
        Args:
            text: Text to extract timestamps from
            
        Returns:
            List of normalized ISO 8601 timestamps
        """
        timestamps = []
        
        for pattern, converter in cls.PATTERNS:
            matches = re.finditer(pattern, text)
            for match in matches:
                try:
                    normalized = converter(match)
                    timestamps.append(normalized)
                except (ValueError, OSError):
                    # Skip invalid timestamps
                    continue
        
        return timestamps
    
    @classmethod
    def get_timestamp_range(cls, text: str) -> Optional[Tuple[str, str]]:
        """
        Get the earliest and latest timestamps from text.
        
        Args:
            text: Text to extract timestamps from
            
        Returns:
            Tuple of (earliest, latest) timestamps or None
        """
        timestamps = cls.extract_timestamps(text)
        
        if not timestamps:
            return None
        
        sorted_timestamps = sorted(timestamps)
        return (sorted_timestamps[0], sorted_timestamps[-1])

def compute_text_hash(text: str) -> str:
    """
    Compute SHA256 hash of text for caching.
    
    Args:
        text: Text to hash
        
    Returns:
        Hex digest of SHA256 hash
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def chunk_text(text: str, chunk_size: int, overlap: int = 0) -> List[Tuple[str, int, int]]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Maximum characters per chunk
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of (chunk_text, start_char, end_char) tuples
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and < chunk_size")
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end]
        chunks.append((chunk, start, end))
        
        # Move to next chunk with overlap
        start += chunk_size - overlap
    
    return chunks

def chunk_by_lines(lines: List[str], max_lines: int, overlap_lines: int = 0) -> List[Tuple[List[str], int, int]]:
    """
    Split lines into overlapping chunks.
    
    Args:
        lines: List of lines
        max_lines: Maximum lines per chunk
        overlap_lines: Number of lines to overlap
        
    Returns:
        List of (chunk_lines, start_line, end_line) tuples
    """
    if max_lines <= 0:
        raise ValueError("max_lines must be positive")
    
    if overlap_lines < 0 or overlap_lines >= max_lines:
        raise ValueError("overlap_lines must be >= 0 and < max_lines")
    
    chunks = []
    start = 0
    total_lines = len(lines)
    
    while start < total_lines:
        end = min(start + max_lines, total_lines)
        chunk = lines[start:end]
        chunks.append((chunk, start + 1, end))  # 1-indexed line numbers
        
        # Move to next chunk with overlap
        start += max_lines - overlap_lines
    
    return chunks

def deduplicate_lines(lines: List[str], keep_order: bool = True) -> List[str]:
    """
    Remove duplicate lines while optionally preserving order.
    
    Args:
        lines: List of lines
        keep_order: Whether to preserve original order
        
    Returns:
        List of unique lines
    """
    if keep_order:
        seen = set()
        result = []
        for line in lines:
            if line not in seen:
                seen.add(line)
                result.append(line)
        return result
    else:
        return list(set(lines))

def batch_items(items: List, batch_size: int) -> List[List]:
    """
    Split items into batches.
    
    Args:
        items: List of items to batch
        batch_size: Size of each batch
        
    Returns:
        List of batches
    """
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    
    batches = []
    for i in range(0, len(items), batch_size):
        batches.append(items[i:i + batch_size])
    
    return batches

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = 'unnamed'
    
    return sanitized
