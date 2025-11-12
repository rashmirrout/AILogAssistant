"""
Configuration management for Log Analytics Assistant.
Loads settings from environment variables and config files.
"""

import os
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
import yaml

# Load environment variables
load_dotenv()


@dataclass
class Settings:
    """Application settings."""
    
    # API Keys
    gemini_api_key: str
    openrouter_api_key: Optional[str]
    
    # Azure OpenAI Configuration
    azure_openai_api_key: Optional[str]
    azure_openai_endpoint: Optional[str]
    azure_openai_deployment: Optional[str]
    azure_openai_api_version: Optional[str]
    
    # Paths
    root_directory: Path
    
    # Chunking
    chunk_size: int
    overlap: int
    
    # Retrieval
    top_k: int
    
    # Embedding
    embedding_default: str
    embedding_batch_size: int
    
    # LLM
    llm_default: str
    llm_temperature: float
    llm_max_tokens: int
    
    # Log files
    log_extensions: List[str]
    
    # Performance
    max_chunk_cache_size: int
    enable_embedding_cache: bool
    
    def __post_init__(self):
        """Ensure root directory exists."""
        self.root_directory = Path(self.root_directory)
        self.root_directory.mkdir(parents=True, exist_ok=True)
        
        # Create issues directory
        issues_dir = self.root_directory / "issues"
        issues_dir.mkdir(exist_ok=True)


def load_settings() -> Settings:
    """Load settings from environment and config files."""
    
    # Load YAML config
    config_path = Path("data/config.yaml")
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Get environment variables
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")  # Optional
    if openrouter_api_key:
        openrouter_api_key = openrouter_api_key.strip()
    
    # Azure OpenAI Configuration (Optional)
    azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if azure_openai_api_key:
        azure_openai_api_key = azure_openai_api_key.strip()
    
    azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    if azure_openai_endpoint:
        azure_openai_endpoint = azure_openai_endpoint.strip()
    
    azure_openai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    if azure_openai_deployment:
        azure_openai_deployment = azure_openai_deployment.strip()
    
    azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview").strip()
    
    root_directory = os.getenv("ROOT_DIRECTORY", "./data")
    
    return Settings(
        gemini_api_key=gemini_api_key,
        openrouter_api_key=openrouter_api_key,
        azure_openai_api_key=azure_openai_api_key,
        azure_openai_endpoint=azure_openai_endpoint,
        azure_openai_deployment=azure_openai_deployment,
        azure_openai_api_version=azure_openai_api_version,
        root_directory=Path(root_directory),
        chunk_size=config.get("chunk_size", 800),
        overlap=config.get("overlap", 100),
        top_k=config.get("top_k", 5),
        embedding_default=config.get("embedding_default", "gemini:text-embedding-004"),
        embedding_batch_size=config.get("embedding_batch_size", 32),
        llm_default=config.get("llm_default", "gemini-1.5-flash"),
        llm_temperature=config.get("llm_temperature", 0.1),
        llm_max_tokens=config.get("llm_max_tokens", 2048),
        log_extensions=config.get("log_extensions", [".log", ".txt", ".jsonl"]),
        max_chunk_cache_size=config.get("max_chunk_cache_size", 10000),
        enable_embedding_cache=config.get("enable_embedding_cache", True)
    )


# Global settings instance
settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings instance."""
    global settings
    if settings is None:
        settings = load_settings()
    return settings
