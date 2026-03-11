"""
LLM Client - Abstraction for Claude API calls
Week 1: Direct calls
Week 2: Will integrate with RAG
Week 3: Will be used by agents
"""

from anthropic import Anthropic
from typing import Optional, Dict, Any
import json
from app.config import get_settings

settings = get_settings()


class LLMClient:
    """
    Wrapper for LLM API calls
    Designed to work with or without RAG/agents
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        context: Optional[str] = None,  # Week 2: RAG will inject context here
    ) -> str:
        """
        Generate text response from LLM
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            temperature: Override default temperature
            max_tokens: Override default max tokens
            context: Additional context (for RAG in Week 2)
        
        Returns:
            Generated text
        """
        
        # Week 2: If RAG is enabled and context provided, prepend it
        if context and settings.ENABLE_RAG:
            full_prompt = f"""Context from knowledge base:
{context}

---

User query: {prompt}

Answer based on the context above."""
        else:
            full_prompt = prompt
        
        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens or self.max_tokens,
            temperature=temperature or self.temperature,
            system=system_prompt or "",
            messages=[
                {"role": "user", "content": full_prompt}
            ]
        )
        
        return response.content[0].text
    
    def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: str = "json"
    ) -> Dict[str, Any]:
        """
        Generate structured output (JSON)
        Used for match scores, analysis results, etc.
        """
        
        structured_system = f"""{system_prompt or ''}

CRITICAL: Respond ONLY with valid {response_format.upper()}. 
No markdown code blocks, no explanations, just the JSON object."""
        
        response_text = self.generate(
            prompt=prompt,
            system_prompt=structured_system
        )
        
        # Parse JSON
        try:
            # Clean up response (remove markdown if present)
            cleaned = response_text.strip()
            
            # Remove markdown code blocks if present
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            cleaned = cleaned.strip()
            
            return json.loads(cleaned)
            
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse LLM response as JSON.\n"
                f"Error: {e}\n"
                f"Response was:\n{response_text}"
            )
    
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ):
        """
        Stream response chunk by chunk
        Used for real-time UI updates (Week 4)
        """
        with self.client.messages.stream(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            for text in stream.text_stream:
                yield text


# Singleton instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create LLM client singleton"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client