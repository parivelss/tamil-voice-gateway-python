"""
Pydantic models for conversational AI
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class ConversationRequest(BaseModel):
    """Request for conversation processing"""
    audio_data: str = Field(description="Base64 encoded audio data")
    session_id: Optional[str] = Field(default=None, description="Session ID for conversation continuity")
    stt_provider: Optional[str] = Field(default="sarvam", description="STT provider to use")
    tts_provider: Optional[str] = Field(default="elevenlabs", description="TTS provider to use")
    llm_provider: Optional[str] = Field(default="gemini", description="LLM provider to use")
    reset_conversation: Optional[bool] = Field(default=False, description="Reset conversation history")
    voice_speed: Optional[float] = Field(default=1.0, ge=0.5, le=2.0, description="TTS voice speed")


class ConversationResponse(BaseModel):
    """Response model for conversational AI"""
    user_transcript: str = Field(description="User's transcribed speech")
    user_language: str = Field(description="Detected language of user speech")
    ai_response_text: str = Field(description="AI's text response")
    ai_response_language: str = Field(description="Language of AI response")
    audio_url: Optional[str] = Field(default=None, description="URL to AI response audio")
    session_id: str = Field(description="Session ID for conversation continuity")
    processing_time_sec: float = Field(description="Total processing time")
    conversation_stats: Dict[str, Any] = Field(description="Conversation statistics")


class ConversationSession(BaseModel):
    """Model for conversation session management"""
    session_id: str
    created_at: str
    last_activity: str
    message_count: int
    languages_used: List[str]
    active: bool = True
