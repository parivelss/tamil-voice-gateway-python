"""
Speech-to-Text data models
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class STTProvider(str, Enum):
    """Available STT providers"""
    SARVAM = "sarvam"
    GOOGLE = "google"
    ELEVENLABS = "elevenlabs"


class STTOptions(BaseModel):
    """STT processing options"""
    language: str = Field(default="auto", description="Language code or 'auto' for detection")
    timestamps: bool = Field(default=False, description="Include word-level timestamps")
    max_alternatives: int = Field(default=1, description="Maximum number of alternative transcriptions")
    provider: STTProvider = Field(default=STTProvider.SARVAM, description="STT provider to use")


class TimestampInfo(BaseModel):
    """Word-level timestamp information"""
    start: float = Field(description="Start time in seconds")
    end: float = Field(description="End time in seconds")
    text: str = Field(description="Word or phrase text")


class STTResult(BaseModel):
    """STT transcription result"""
    text: str = Field(description="Transcribed text")
    confidence: float = Field(description="Confidence score (0.0 to 1.0)")
    detected_language: str = Field(description="Detected language code")
    timestamps: Optional[List[TimestampInfo]] = Field(default=None, description="Word-level timestamps")
    alternatives: Optional[List[str]] = Field(default=None, description="Alternative transcriptions")
    provider: Optional[str] = Field(default=None, description="STT provider used")


class ListenRequest(BaseModel):
    """Request model for /listen endpoint"""
    audio_base64: Optional[str] = Field(default=None, description="Base64 encoded audio data")
    stt_provider: STTProvider = Field(default=STTProvider.SARVAM, description="STT provider preference")
    timestamps: bool = Field(default=False, description="Include timestamps in response")


class ListenResponse(BaseModel):
    """Response model for /listen endpoint"""
    success: bool = Field(description="Request success status")
    english_transcript: str = Field(description="English transcript for conversation")
    original_language: str = Field(description="Detected original language")
    original_text: str = Field(description="Original transcribed text")
    confidence: float = Field(description="Transcription confidence")
    processing_time_sec: float = Field(description="Processing time in seconds")
    stt_provider: str = Field(description="STT provider used")
    timestamps: Optional[List[TimestampInfo]] = Field(default=None, description="Word-level timestamps")
