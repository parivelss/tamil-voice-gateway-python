"""
Sarvam AI Speech-to-Text Adapter
Optimized for Indian languages and code-switching
"""

import httpx
import logging
from typing import Optional, Dict, Any, List
from io import BytesIO

from app.core.config import settings
from app.models.stt import STTResult, STTOptions
from app.adapters.base import STTAdapter

logger = logging.getLogger(__name__)


class SarvamSTTAdapter(STTAdapter):
    """Sarvam AI STT adapter for Indian languages"""
    
    def __init__(self):
        self.api_key = settings.SARVAM_API_KEY
        self.base_url = "https://api.sarvam.ai/speech-to-text/transcribe"
        
        if not self.api_key:
            raise ValueError("SARVAM_API_KEY is required for Sarvam STT adapter")
    
    async def transcribe(self, audio_data: bytes, options: STTOptions) -> STTResult:
        """
        Transcribe audio using Sarvam AI STT
        
        Args:
            audio_data: Audio file bytes
            options: STT options
            
        Returns:
            STTResult with transcription
        """
        try:
            logger.info(f"Starting Sarvam STT transcription", extra={
                "audio_size": len(audio_data),
                "language": options.language,
                "timestamps": options.timestamps
            })
            
            # Prepare form data
            files = {
                "file": ("audio.wav", BytesIO(audio_data), "audio/wav")
            }
            
            data = {
                "model": "saarika:v2.5",  # Optimized for Indian languages
                "language_code": self._map_language_code(options.language),
            }
            
            if options.timestamps:
                data["with_timestamps"] = "true"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    files=files,
                    data=data,
                    headers=headers
                )
                
                if not response.is_success:
                    error_text = response.text
                    logger.error(f"Sarvam STT API error: {response.status_code} - {error_text}")
                    raise Exception(f"Sarvam STT API error: {response.status_code} - {error_text}")
                
                result = response.json()
                
                if not result.get("transcript"):
                    raise Exception("No transcript returned from Sarvam STT")
                
                # Map response to STTResult
                detected_language = self._map_sarvam_language_to_standard(
                    result.get("language_code")
                )
                
                stt_result = STTResult(
                    text=result["transcript"],
                    confidence=0.9,  # Sarvam doesn't provide confidence scores
                    detected_language=detected_language,
                    timestamps=self._parse_timestamps(result.get("timestamps")) if options.timestamps else None
                )
                
                logger.info("Sarvam STT transcription completed", extra={
                    "detected_language": detected_language,
                    "text_length": len(stt_result.text),
                    "has_timestamps": bool(stt_result.timestamps)
                })
                
                return stt_result
                
        except Exception as error:
            logger.error(f"Sarvam STT transcription failed: {str(error)}")
            raise Exception(f"Sarvam speech-to-text failed: {str(error)}")
    
    def _map_language_code(self, language: str) -> str:
        """Map language code to Sarvam format"""
        language_map = {
            "auto": "unknown",
            "ta": "ta",
            "en": "en",
            "hi": "hi",
            "bn": "bn",
            "gu": "gu",
            "kn": "kn",
            "ml": "ml",
            "mr": "mr",
            "or": "or",
            "pa": "pa",
            "te": "te"
        }
        return language_map.get(language, "unknown")
    
    def _map_sarvam_language_to_standard(self, sarvam_lang: Optional[str]) -> str:
        """Map Sarvam language code to standard format"""
        if not sarvam_lang:
            return "en"
        
        # Extract primary language from BCP-47 code
        primary_lang = sarvam_lang.split("-")[0].lower()
        
        if primary_lang in ["ta", "tamil"]:
            return "ta"
        
        return "en"  # Default to English
    
    def _parse_timestamps(self, timestamps_data: Optional[List[Dict]]) -> Optional[List[Dict[str, Any]]]:
        """Parse timestamps from Sarvam response"""
        if not timestamps_data:
            return None
        
        return [
            {
                "start": ts.get("start", 0),
                "end": ts.get("end", 0),
                "text": ts.get("text", "")
            }
            for ts in timestamps_data
        ]
