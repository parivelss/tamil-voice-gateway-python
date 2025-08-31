"""
Google Cloud Speech-to-Text Adapter
"""

import logging
import time
from typing import Optional, List, Dict, Any
from google.cloud import speech
import io

from app.core.config import settings
from app.models.stt import STTResult, STTOptions, TimestampInfo
from app.adapters.base import STTAdapter

logger = logging.getLogger(__name__)


class GoogleSTTAdapter(STTAdapter):
    """Google Cloud STT adapter"""
    
    def __init__(self):
        self.client = speech.SpeechClient()
        self.project_id = settings.GOOGLE_PROJECT_ID
        
    async def transcribe(self, audio_data: bytes, options: STTOptions) -> STTResult:
        """
        Transcribe audio using Google Cloud STT
        
        Args:
            audio_data: Audio file bytes
            options: STT options
            
        Returns:
            STTResult with transcription
        """
        start_time = time.time()
        try:
            logger.info("Starting Google STT transcription", extra={
                "audio_size": len(audio_data),
                "language": options.language,
                "timestamps": options.timestamps
            })
            
            # Simple validation - just check if we have audio data
            if len(audio_data) < 10:
                logger.info("No speech detected in audio, returning empty result")
                return STTResult(
                    text="",
                    confidence=0.0,
                    detected_language=options.language or "en",
                    provider="google",
                    processing_time=time.time() - start_time
                )
            
            # Use automatic encoding detection - let Google handle it
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,
                language_code=self._map_language_code(options.language),
                alternative_language_codes=[settings.GOOGLE_STT_ALT_LANGS] if options.language == "auto" else [],
                max_alternatives=options.max_alternatives,
                enable_word_time_offsets=options.timestamps,
                enable_automatic_punctuation=True
            )
            
            audio = speech.RecognitionAudio(content=audio_data)
            
            # Perform transcription
            response = self.client.recognize(config=config, audio=audio)
            
            # Handle empty results (silence or no speech detected)
            if not response.results:
                logger.info("No speech detected in audio, returning empty result")
                return STTResult(
                    text="",
                    confidence=0.0,
                    detected_language=options.language or "en",
                    provider="google",
                    processing_time=time.time() - start_time
                )
            
            # Get best result
            result = response.results[0]
            alternative = result.alternatives[0]
            
            # Detect language from response
            detected_language = self._extract_language_from_response(response, options.language)
            
            # Parse timestamps if requested
            timestamps = None
            if options.timestamps and alternative.words:
                timestamps = [
                    TimestampInfo(
                        start=word.start_time.total_seconds(),
                        end=word.end_time.total_seconds(),
                        text=word.word
                    )
                    for word in alternative.words
                ]
            
            # Get alternatives
            alternatives = [alt.transcript for alt in result.alternatives[1:]] if len(result.alternatives) > 1 else None
            
            stt_result = STTResult(
                text=alternative.transcript,
                confidence=alternative.confidence,
                detected_language=detected_language,
                timestamps=timestamps,
                alternatives=alternatives,
                provider="google"
            )
            
            logger.info("Google STT transcription completed", extra={
                "detected_language": detected_language,
                "text_length": len(stt_result.text),
                "confidence": stt_result.confidence,
                "has_timestamps": bool(timestamps)
            })
            
            return stt_result
            
        except Exception as error:
            logger.error(f"Google STT transcription failed: {str(error)}")
            raise Exception(f"Google speech-to-text failed: {str(error)}")
    
    def _map_language_code(self, language: str) -> str:
        """Map language code to Google STT format"""
        if language == "auto":
            return settings.GOOGLE_STT_LANGUAGE
        
        language_map = {
            "ta": "ta-IN",
            "en": "en-IN",
            "hi": "hi-IN",
            "bn": "bn-IN",
            "gu": "gu-IN",
            "kn": "kn-IN",
            "ml": "ml-IN",
            "mr": "mr-IN",
            "or": "or-IN",
            "pa": "pa-IN",
            "te": "te-IN"
        }
        
        return language_map.get(language, "en-IN")
    
    def _extract_language_from_response(self, response, requested_language: str) -> str:
        """Extract detected language from Google STT response"""
        if requested_language != "auto":
            return requested_language
        
        # Try to get language from response
        if response.results and response.results[0].language_code:
            lang_code = response.results[0].language_code
            if lang_code.startswith("ta"):
                return "ta"
            elif lang_code.startswith("en"):
                return "en"
        
        # Default based on primary language setting
        if settings.GOOGLE_STT_LANGUAGE.startswith("ta"):
            return "ta"
        
        return "en"
