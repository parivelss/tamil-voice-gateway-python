"""
Base classes for STT, TTS, and Translation adapters
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from app.models.stt import STTResult, STTOptions
from app.models.tts import TTSResult, TTSOptions
from app.models.translation import TranslationResult, TranslationOptions
from app.models.llm import LLMResult, ConversationMessage


class STTAdapter(ABC):
    """Base class for Speech-to-Text adapters"""
    
    @abstractmethod
    async def transcribe(self, audio_data: bytes, options: STTOptions) -> STTResult:
        """Transcribe audio to text"""
        pass


class TTSAdapter(ABC):
    """Base class for Text-to-Speech adapters"""
    
    @abstractmethod
    async def synthesize(self, text: str, language: str, options: TTSOptions) -> TTSResult:
        """Synthesize text to speech"""
        pass


class TranslationAdapter(ABC):
    """Base class for Translation adapters"""
    
    @abstractmethod
    async def translate(self, text: str, target_language: str, source_language: Optional[str] = None) -> TranslationResult:
        """Translate text between languages"""
        pass
    
    @abstractmethod
    async def detect_language(self, text: str) -> str:
        """Detect language of text"""
        pass


class LLMAdapter(ABC):
    """Base class for Large Language Model adapters"""
    
    @abstractmethod
    async def chat(self, user_message: str, language: str = "auto", conversation_history: Optional[List[ConversationMessage]] = None) -> str:
        """Generate chat response"""
        pass
