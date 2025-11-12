"""
Model strategy registry for embedding and LLM providers.
Implements the strategy pattern for configurable model selection.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Type
import numpy as np

class EmbeddingStrategy(ABC):
    """Abstract base class for embedding strategies."""
    
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            NumPy array of shape (len(texts), embedding_dim)
        """
        pass
    
    @abstractmethod
    def get_embedding_dim(self) -> int:
        """Get the dimension of embeddings produced by this strategy."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name identifier."""
        pass

class LLMStrategy(ABC):
    """Abstract base class for LLM strategies."""
    
    @abstractmethod
    def generate(self, prompt: str, temperature: float = 0.1, max_tokens: int = 2048) -> str:
        """
        Generate text response from prompt.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name identifier."""
        pass

class GeminiEmbeddingStrategy(EmbeddingStrategy):
    """Gemini embedding strategy using Google's text-embedding-004."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model_name = "models/text-embedding-004"
        self._embedding_dim = 768
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using Gemini API."""
        import google.generativeai as genai
        
        genai.configure(api_key=self.api_key)
        
        embeddings = []
        for text in texts:
            result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type="retrieval_document"
            )
            embeddings.append(result['embedding'])
        
        return np.array(embeddings, dtype=np.float32)
    
    def get_embedding_dim(self) -> int:
        return self._embedding_dim
    
    def get_model_name(self) -> str:
        return "gemini:text-embedding-004"

class SentenceTransformerStrategy(EmbeddingStrategy):
    """Local sentence transformer embedding strategy."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        
        self.model_name_short = model_name
        self.model = SentenceTransformer(model_name)
        self._embedding_dim = self.model.get_sentence_embedding_dimension()
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using SentenceTransformer."""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.astype(np.float32)
    
    def get_embedding_dim(self) -> int:
        return self._embedding_dim
    
    def get_model_name(self) -> str:
        return f"st:{self.model_name_short}"

class GeminiChatStrategy(LLMStrategy):
    """Gemini chat strategy for text generation."""
    
    def __init__(self, api_key: str, model_variant: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_variant = model_variant
    
    def generate(self, prompt: str, temperature: float = 0.1, max_tokens: int = 2048) -> str:
        """Generate response using Gemini API."""
        import google.generativeai as genai
        
        genai.configure(api_key=self.api_key)
        
        model = genai.GenerativeModel(self.model_variant)
        
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens
        )
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return response.text
    
    def get_model_name(self) -> str:
        return self.model_variant

class OpenRouterChatStrategy(LLMStrategy):
    """OpenRouter chat strategy for text generation via OpenAI-compatible API."""
    
    def __init__(self, api_key: str, model_variant: str):
        self.api_key = api_key
        self.model_variant = model_variant
    
    def generate(self, prompt: str, temperature: float = 0.1, max_tokens: int = 2048) -> str:
        """Generate response using OpenRouter API."""
        import requests
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/yourusername/ailogassistant",
            "X-Title": "AI Log Assistant"
        }
        
        payload = {
            "model": self.model_variant,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise ValueError(f"OpenRouter API error {response.status_code}: {response.text}")
        
        result = response.json()
        
        if "choices" not in result or len(result["choices"]) == 0:
            raise ValueError(f"Invalid OpenRouter response: {result}")
        
        return result["choices"][0]["message"]["content"]
    
    def get_model_name(self) -> str:
        return f"openrouter:{self.model_variant}"

class AzureOpenAIChatStrategy(LLMStrategy):
    """Azure OpenAI chat strategy for text generation."""
    
    def __init__(self, api_key: str, endpoint: str, deployment: str, api_version: str):
        self.api_key = api_key
        self.endpoint = endpoint.rstrip('/')
        self.deployment = deployment
        self.api_version = api_version
    
    def generate(self, prompt: str, temperature: float = 0.1, max_tokens: int = 2048) -> str:
        """Generate response using Azure OpenAI API."""
        import requests
        
        url = f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"
        
        print(f"   🌐 Azure OpenAI API URL: {url}")
        print(f"   🔑 API Key (last 4): ...{self.api_key[-4:] if len(self.api_key) >= 4 else '****'}")
        print(f"   📋 Deployment: {self.deployment}")
        
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise ValueError(f"Azure OpenAI API error {response.status_code}: {response.text}")
        
        result = response.json()
        
        if "choices" not in result or len(result["choices"]) == 0:
            raise ValueError(f"Invalid Azure OpenAI response: {result}")
        
        return result["choices"][0]["message"]["content"]
    
    def get_model_name(self) -> str:
        return f"azure:{self.deployment}"

class ModelRegistry:
    """Registry for available embedding and LLM models."""
    
    # Embedding model registry
    EMBEDDING_MODELS: Dict[str, Type[EmbeddingStrategy]] = {
        "gemini:text-embedding-004": GeminiEmbeddingStrategy,
        "st:all-MiniLM-L6-v2": SentenceTransformerStrategy,
        "st:all-mpnet-base-v2": SentenceTransformerStrategy,
    }
    
    # LLM model registry (populated dynamically for Gemini models)
    LLM_MODELS: Dict[str, Type[LLMStrategy]] = {
        "gemini-1.5-flash": GeminiChatStrategy,  # Default fallback
    }
    _gemini_models_loaded = False
    _openrouter_models_registered = False
    
    # Popular OpenRouter models (static list - can be extended)
    OPENROUTER_MODELS = [
        "openai/gpt-4o-mini",
        "openai/gpt-4o",
        "openai/gpt-3.5-turbo",
        "anthropic/claude-3.5-sonnet",
        "anthropic/claude-3-haiku",
        "meta-llama/llama-3.1-8b-instruct",
        "meta-llama/llama-3.1-70b-instruct",
        "google/gemini-pro-1.5",
        "google/gemini-flash-1.5",
        "mistralai/mistral-7b-instruct",
        "qwen/qwen-2-7b-instruct",
    ]
    
    @classmethod
    def register_openrouter_models(cls) -> None:
        """Register OpenRouter models in the registry."""
        if cls._openrouter_models_registered:
            return
        
        for model_id in cls.OPENROUTER_MODELS:
            cls.LLM_MODELS[f"openrouter:{model_id}"] = OpenRouterChatStrategy
        
        cls._openrouter_models_registered = True
        print(f"✓ Registered {len(cls.OPENROUTER_MODELS)} OpenRouter models")
    
    @classmethod
    def refresh_gemini_models(cls, api_key: str) -> None:
        """
        Discover and register available Gemini models dynamically.
        
        Args:
            api_key: Gemini API key
        """
        if cls._gemini_models_loaded:
            return  # Already loaded
            
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=api_key)
            
            # List all available models
            available_models = genai.list_models()
            
            # Remove only Gemini models (keep OpenRouter)
            cls.LLM_MODELS = {k: v for k, v in cls.LLM_MODELS.items() if not k.startswith('gemini')}
            
            # Filter models that support generateContent
            for model in available_models:
                if 'generateContent' in model.supported_generation_methods:
                    # Extract model name (e.g., "models/gemini-1.5-flash" -> "gemini-1.5-flash")
                    model_name = model.name.replace('models/', '')
                    
                    # Only register Gemini models for chat
                    if model_name.startswith('gemini'):
                        cls.LLM_MODELS[model_name] = GeminiChatStrategy
            
            cls._gemini_models_loaded = True
            
            print(f"✓ Loaded {len([k for k in cls.LLM_MODELS if k.startswith('gemini')])} Gemini models")
            
        except Exception as e:
            print(f"⚠ Warning: Failed to load Gemini models dynamically: {e}")
            print("  Using fallback: gemini-1.5-flash only")
            # Fallback to default model
            if 'gemini-1.5-flash' not in cls.LLM_MODELS:
                cls.LLM_MODELS["gemini-1.5-flash"] = GeminiChatStrategy
            cls._gemini_models_loaded = True
    
    @classmethod
    def get_embedding_strategy(cls, model_name: str, api_key: str = None) -> EmbeddingStrategy:
        """
        Get an embedding strategy instance.
        
        Args:
            model_name: Model identifier (e.g., "gemini:text-embedding-004")
            api_key: API key for cloud models
            
        Returns:
            EmbeddingStrategy instance
            
        Raises:
            ValueError: If model not found
        """
        if model_name not in cls.EMBEDDING_MODELS:
            raise ValueError(f"Unknown embedding model: {model_name}. Available: {list(cls.EMBEDDING_MODELS.keys())}")
        
        strategy_class = cls.EMBEDDING_MODELS[model_name]
        
        # Instantiate based on model type
        if model_name.startswith("gemini:"):
            if not api_key:
                raise ValueError("API key required for Gemini models")
            return strategy_class(api_key)
        elif model_name.startswith("st:"):
            # Extract actual model name
            actual_model = model_name.split(":", 1)[1]
            return strategy_class(actual_model)
        else:
            return strategy_class()
    
    @classmethod
    def register_azure_model(cls, deployment_name: str) -> None:
        """Register Azure OpenAI deployment in the registry."""
        model_key = f"azure:{deployment_name}"
        if model_key not in cls.LLM_MODELS:
            cls.LLM_MODELS[model_key] = AzureOpenAIChatStrategy
            print(f"✓ Registered Azure OpenAI deployment: {deployment_name}")
    
    @classmethod
    def get_llm_strategy(
        cls, 
        model_name: str, 
        gemini_api_key: str = None, 
        openrouter_api_key: str = None,
        azure_openai_api_key: str = None,
        azure_openai_endpoint: str = None,
        azure_openai_deployment: str = None,
        azure_openai_api_version: str = None
    ) -> LLMStrategy:
        """
        Get an LLM strategy instance.
        
        Args:
            model_name: Model identifier (e.g., "gemini-1.5-flash", "openrouter:openai/gpt-4o-mini", "azure:deployment-name")
            gemini_api_key: Gemini API key
            openrouter_api_key: OpenRouter API key
            azure_openai_api_key: Azure OpenAI API key
            azure_openai_endpoint: Azure OpenAI endpoint
            azure_openai_deployment: Azure OpenAI deployment name
            azure_openai_api_version: Azure OpenAI API version
            
        Returns:
            LLMStrategy instance
            
        Raises:
            ValueError: If model not found or API key missing
        """
        print(f"\n🔍 LLM Strategy Selection:")
        print(f"   Requested model: {model_name}")
        
        # Ensure Gemini models are loaded
        if gemini_api_key and not cls._gemini_models_loaded:
            cls.refresh_gemini_models(gemini_api_key)
        
        # Register OpenRouter models if key is available
        if openrouter_api_key and not cls._openrouter_models_registered:
            cls.register_openrouter_models()
        
        # Register Azure model if credentials are available
        if model_name.startswith("azure:") and azure_openai_deployment:
            cls.register_azure_model(azure_openai_deployment)
            
            # Check for mismatch between requested model and deployment
            requested_deployment = model_name.replace("azure:", "")
            if requested_deployment != azure_openai_deployment:
                print(f"   ⚠️  WARNING: Model name mismatch!")
                print(f"   Requested: azure:{requested_deployment}")
                print(f"   Deployment: {azure_openai_deployment}")
                print(f"   Using deployment: {azure_openai_deployment}")
        
        # Determine provider
        if model_name.startswith("gemini"):
            provider = "Gemini"
        elif model_name.startswith("openrouter:"):
            provider = "OpenRouter"
        elif model_name.startswith("azure:"):
            provider = "Azure OpenAI"
        else:
            provider = "Unknown"
        
        print(f"   Provider: {provider}")
        print(f"   Model registered: {model_name in cls.LLM_MODELS}")
        
        # If model not found, try to use first available model as fallback
        if model_name not in cls.LLM_MODELS:
            print(f"   ⚠️  Model '{model_name}' not found in registry!")
            print(f"   Available models: {list(cls.LLM_MODELS.keys())}")
            
            if cls.LLM_MODELS:
                fallback_model = list(cls.LLM_MODELS.keys())[0]
                print(f"   ➡️  Using fallback model: {fallback_model}")
                model_name = fallback_model
            else:
                raise ValueError(f"Unknown LLM model: {model_name}. No models available!")
        else:
            print(f"   ✅ Model found in registry")
        
        strategy_class = cls.LLM_MODELS[model_name]
        print(f"   Strategy class: {strategy_class.__name__}")
        
        # Instantiate based on model type
        if model_name.startswith("gemini"):
            if not gemini_api_key:
                raise ValueError("Gemini API key required for Gemini models")
            return strategy_class(gemini_api_key, model_name)
        elif model_name.startswith("openrouter:"):
            if not openrouter_api_key:
                raise ValueError("OpenRouter API key required for OpenRouter models")
            # Extract actual model name (remove "openrouter:" prefix)
            actual_model = model_name.replace("openrouter:", "")
            return strategy_class(openrouter_api_key, actual_model)
        elif model_name.startswith("azure:"):
            if not azure_openai_api_key or not azure_openai_endpoint or not azure_openai_deployment:
                raise ValueError("Azure OpenAI credentials (api_key, endpoint, deployment) required for Azure models")
            return strategy_class(
                azure_openai_api_key,
                azure_openai_endpoint,
                azure_openai_deployment,
                azure_openai_api_version or "2024-02-15-preview"
            )
        else:
            return strategy_class()
    
    @classmethod
    def list_embedding_models(cls) -> List[str]:
        """List available embedding models."""
        return list(cls.EMBEDDING_MODELS.keys())
    
    @classmethod
    def list_llm_models(cls) -> List[str]:
        """List available LLM models."""
        return list(cls.LLM_MODELS.keys())
