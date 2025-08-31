"""
Large Language Model data models
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class LLMProvider(str, Enum):
    """Available LLM providers"""
    OPENAI = "openai"
    GEMINI = "gemini"


class ConversationMessage(BaseModel):
    """Conversation message"""
    role: str = Field(description="Message role: user or assistant")
    content: str = Field(description="Message content")
    timestamp: Optional[float] = Field(default=None, description="Message timestamp")


class LLMResult(BaseModel):
    """LLM response result"""
    text: str = Field(description="Generated response text")
    provider: str = Field(description="LLM provider used")
    model: str = Field(description="Model used")
    tokens_used: Optional[int] = Field(default=None, description="Tokens consumed")
