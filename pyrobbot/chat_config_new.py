"""Chat configuration for both OpenAI and Gemini models."""

import os
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field

class GeminiConfig(BaseModel):
    """Configuration for Gemini API."""
    
    model: Literal["gemini-pro"] = "gemini-pro"
    temperature: float = Field(0.7, ge=0.0, le=1.0)
    top_p: float = Field(0.8, ge=0.0, le=1.0)
    top_k: int = Field(40, ge=1)
    max_output_tokens: int = Field(2048, ge=1)
    api_key: Optional[str] = Field(None, description="Gemini API key")

class OpenAIConfig(BaseModel):
    """Configuration for OpenAI API."""
    
    model: Literal["gpt-3.5-turbo", "gpt-4"] = "gpt-3.5-turbo"
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    top_p: float = Field(1.0, ge=0.0, le=1.0)
    presence_penalty: float = Field(0.0, ge=-2.0, le=2.0)
    frequency_penalty: float = Field(0.0, ge=-2.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1)
    api_key: Optional[str] = Field(None, description="OpenAI API key")

class ChatConfig(BaseModel):
    """Main chat configuration that can use either OpenAI or Gemini."""
    
    provider: Literal["openai", "gemini"] = "gemini"
    openai_config: Optional[OpenAIConfig] = None
    gemini_config: Optional[GeminiConfig] = Field(
        default_factory=GeminiConfig,
        description="Gemini-specific configuration"
    )
    
    def get_api_key(self) -> str:
        """Get the API key for the selected provider."""
        if self.provider == "openai":
            return self.openai_config.api_key or os.getenv("OPENAI_API_KEY")
        else:
            return self.gemini_config.api_key or os.getenv("GOOGLE_API_KEY")

    class Config:
        use_enum_values = True