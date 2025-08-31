"""
Text-to-Speech data models
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum


class TTSProvider(str, Enum):
    """Available TTS providers"""
    ELEVENLABS = "elevenlabs"
    GOOGLE = "google"
    LOCAL = "local"


class TTSOptions(BaseModel):
    """TTS processing options"""
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed multiplier")
    voice_id: Optional[str] = Field(default=None, description="Specific voice ID to use")
    model: Optional[str] = Field(default=None, description="TTS model to use")
    provider: TTSProvider = Field(default=TTSProvider.ELEVENLABS, description="TTS provider to use")


class TTSResult(BaseModel):
    """TTS synthesis result"""
    audio_data: bytes = Field(description="Generated audio data")
    audio_format: str = Field(description="Audio format (mp3, wav, etc.)")
    duration_sec: Optional[float] = Field(default=None, description="Audio duration in seconds")
    provider: Optional[str] = Field(default=None, description="TTS provider used")


class SpeakRequest(BaseModel):
    """Request model for /speak endpoint"""
    english_text: str = Field(min_length=1, description="English text to convert to speech")
    target_language: str = Field(default="ta", description="Target language (ta or en)")
    voice_provider: TTSProvider = Field(default=TTSProvider.ELEVENLABS, description="TTS provider")
    voice_speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed")


class SpeakResponse(BaseModel):
    """Response model for /speak endpoint (JSON preview)"""
    success: bool = Field(description="Request success status")
    audio_base64: str = Field(description="Base64 encoded audio data")
    final_text: str = Field(description="Final text that was synthesized")
    final_language: str = Field(description="Final language of synthesis")
    original_text: str = Field(description="Original English input text")
    processing_time_sec: float = Field(description="Processing time in seconds")
    audio_size_bytes: int = Field(description="Audio file size in bytes")
