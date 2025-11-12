"""
LLM connector for generating responses using configured LLM models.
Includes retry logic and error handling.
"""

import json
import time
from typing import Dict, List, Optional
from backend.config import get_settings
from backend.models_registry import ModelRegistry
from backend.models import Chunk

class LLMConnector:
    """Connector for LLM APIs with retry logic."""
    
    def __init__(self):
        self.settings = get_settings()
    
    def generate_response(
        self,
        context_chunks: List[Chunk],
        user_query: str,
        llm_model: Optional[str] = None,
        max_retries: int = 3
    ) -> Dict[str, any]:
        """
        Generate response using LLM with context from retrieved chunks.
        
        Args:
            context_chunks: List of relevant chunks
            user_query: User's question
            llm_model: LLM model to use (defaults to config setting)
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dict with 'answer' and 'references' keys
        """
        # Construct prompt
        prompt = self._build_prompt(context_chunks, user_query)
        
        # Get LLM strategy
        model_name = llm_model or self.settings.llm_default
        
        print(f"\n💬 Generating LLM Response:")
        print(f"   Query: {user_query[:100]}{'...' if len(user_query) > 100 else ''}")
        print(f"   Context chunks: {len(context_chunks)}")
        
        strategy = ModelRegistry.get_llm_strategy(
            model_name, 
            gemini_api_key=self.settings.gemini_api_key,
            openrouter_api_key=self.settings.openrouter_api_key,
            azure_openai_api_key=self.settings.azure_openai_api_key,
            azure_openai_endpoint=self.settings.azure_openai_endpoint,
            azure_openai_deployment=self.settings.azure_openai_deployment,
            azure_openai_api_version=self.settings.azure_openai_api_version
        )
        
        print(f"   ✅ Strategy initialized: {strategy.__class__.__name__}")
        
        # Retry logic with exponential backoff
        last_error = None
        for attempt in range(max_retries):
            try:
                print(f"   🔄 Attempt {attempt + 1}/{max_retries}: Calling LLM API...")
                
                response_text = strategy.generate(
                    prompt,
                    temperature=self.settings.llm_temperature,
                    max_tokens=self.settings.llm_max_tokens
                )
                
                print(f"   ✅ Response received ({len(response_text)} chars)")
                
                # Parse response
                return self._parse_response(response_text, context_chunks)
                
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                
                # Check if it's a 404 or "not found" error (model doesn't exist)
                if '404' in error_str or 'not found' in error_str or 'is not found' in error_str:
                    print(f"⚠ Model error: {e}")
                    
                    # Try to use fallback model immediately (don't retry)
                    if model_name != self.settings.llm_default:
                        print(f"  Switching to fallback model: {self.settings.llm_default}")
                        try:
                            fallback_strategy = ModelRegistry.get_llm_strategy(
                                self.settings.llm_default,
                                gemini_api_key=self.settings.gemini_api_key,
                                openrouter_api_key=self.settings.openrouter_api_key,
                                azure_openai_api_key=self.settings.azure_openai_api_key,
                                azure_openai_endpoint=self.settings.azure_openai_endpoint,
                                azure_openai_deployment=self.settings.azure_openai_deployment,
                                azure_openai_api_version=self.settings.azure_openai_api_version
                            )
                            response_text = fallback_strategy.generate(
                                prompt,
                                temperature=self.settings.llm_temperature,
                                max_tokens=self.settings.llm_max_tokens
                            )
                            return self._parse_response(response_text, context_chunks)
                        except Exception as fallback_error:
                            print(f"  Fallback also failed: {fallback_error}")
                            last_error = fallback_error
                    
                    # If fallback failed or was same model, break retry loop
                    break
                
                if attempt < max_retries - 1:
                    # Exponential backoff for transient errors
                    wait_time = 2 ** attempt
                    print(f"LLM API error (attempt {attempt + 1}/{max_retries}): {e}")
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"LLM API failed after {max_retries} attempts")
        
        # If all retries failed, return fallback response
        return self._generate_fallback_response(context_chunks, user_query, str(last_error))
    
    def _build_prompt(self, context_chunks: List[Chunk], user_query: str) -> str:
        """
        Build prompt for LLM.
        
        Args:
            context_chunks: Relevant chunks
            user_query: User's question
            
        Returns:
            Formatted prompt
        """
        # Format context
        context_parts = []
        for idx, chunk in enumerate(context_chunks):
            context_parts.append(
                f"[Chunk {idx + 1}] {chunk.source_file} (lines {chunk.start_line}-{chunk.end_line}):\n"
                f"{chunk.text}\n"
            )
        
        context_text = "\n".join(context_parts)
        
        # Build full prompt
        prompt = f"""You are an expert log analyst. Your task is to analyze log file excerpts and answer questions about them.

CONTEXT (Log Excerpts):
{context_text}

USER QUERY:
{user_query}

INSTRUCTIONS:
1. Provide a concise, evidence-backed answer based ONLY on the provided log excerpts
2. Reference specific files and line ranges when citing evidence
3. If the logs don't contain enough information to answer the question, say so
4. Format your response as JSON with the following structure:
{{
  "answer": "Your detailed answer here",
  "references": ["file1.log: lines 10-20", "file2.log: lines 45-60"]
}}

RESPONSE (JSON):"""
        
        return prompt
    
    def _parse_response(self, response_text: str, context_chunks: List[Chunk]) -> Dict[str, any]:
        """
        Parse LLM response into structured format.
        
        Args:
            response_text: Raw LLM response
            context_chunks: Context chunks used
            
        Returns:
            Parsed response dict
        """
        # Try to parse as JSON
        try:
            # Clean response text (remove markdown code blocks if present)
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()
            
            parsed = json.loads(clean_text)
            
            # Validate structure
            if "answer" not in parsed:
                raise ValueError("Missing 'answer' key in response")
            
            return {
                "answer": parsed.get("answer", ""),
                "references": parsed.get("references", []),
                "context_chunks": [chunk.dict() for chunk in context_chunks]
            }
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Failed to parse JSON response: {e}")
            
            # Fallback: extract answer using heuristics
            return self._extract_answer_heuristic(response_text, context_chunks)
    
    def _extract_answer_heuristic(self, response_text: str, context_chunks: List[Chunk]) -> Dict[str, any]:
        """
        Extract answer using heuristics when JSON parsing fails.
        
        Args:
            response_text: Raw response text
            context_chunks: Context chunks
            
        Returns:
            Best-effort parsed response
        """
        # Try to extract JSON-like content
        import re
        
        # Look for answer field
        answer_match = re.search(r'"answer"\s*:\s*"([^"]+)"', response_text, re.DOTALL)
        answer = answer_match.group(1) if answer_match else response_text
        
        # Look for references
        refs_match = re.search(r'"references"\s*:\s*\[(.*?)\]', response_text, re.DOTALL)
        references = []
        if refs_match:
            refs_text = refs_match.group(1)
            references = re.findall(r'"([^"]+)"', refs_text)
        
        return {
            "answer": answer,
            "references": references,
            "context_chunks": [chunk.dict() for chunk in context_chunks]
        }
    
    def _generate_fallback_response(self, context_chunks: List[Chunk], user_query: str, error: str) -> Dict[str, any]:
        """
        Generate fallback response when LLM fails.
        
        Args:
            context_chunks: Context chunks
            user_query: User's question
            error: Error message
            
        Returns:
            Fallback response
        """
        # Create a basic summary of context
        file_summary = {}
        for chunk in context_chunks:
            if chunk.source_file not in file_summary:
                file_summary[chunk.source_file] = []
            file_summary[chunk.source_file].append(f"lines {chunk.start_line}-{chunk.end_line}")
        
        summary_parts = []
        for file, ranges in file_summary.items():
            summary_parts.append(f"- {file}: {', '.join(ranges)}")
        
        answer = f"""⚠️ LLM service temporarily unavailable. 

However, I found relevant log excerpts that may help answer your question:

{chr(10).join(summary_parts)}

Please review the context chunks below for details.

Error: {error}"""
        
        return {
            "answer": answer,
            "references": [f"{chunk.source_file}: lines {chunk.start_line}-{chunk.end_line}" for chunk in context_chunks],
            "context_chunks": [chunk.dict() for chunk in context_chunks],
            "fallback": True
        }
