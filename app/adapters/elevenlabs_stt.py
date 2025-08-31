"""
ElevenLabs Speech-to-Text Adapter
"""

import logging
import ssl
import aiohttp
from typing import Optional, List, Dict, Any

from app.core.config import settings
from app.models.stt import STTResult, STTOptions, TimestampInfo
from app.adapters.base import STTAdapter

logger = logging.getLogger(__name__)


class ElevenLabsSTTAdapter(STTAdapter):
    """ElevenLabs STT adapter"""
    
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        
    async def transcribe(self, audio_data: bytes, options: STTOptions) -> STTResult:
        """
        Transcribe audio using ElevenLabs STT
        
        Args:
            audio_data: Audio file bytes
            options: STT options
            
        Returns:
            STTResult with transcription
        """
        try:
            logger.info("Starting ElevenLabs STT transcription", extra={
                "audio_size": len(audio_data),
                "language": options.language
            })
            
            # ElevenLabs STT endpoint
            url = f"{self.base_url}/speech-to-text"
            
            headers = {
                "xi-api-key": self.api_key,
            }
            
            # Prepare form data
            data = aiohttp.FormData()
            data.add_field('audio', audio_data, filename='audio.webm', content_type='audio/webm')
            data.add_field('model_id', 'eleven_multilingual_v2')
            
            # Add language if specified
            if options.language and options.language != "auto":
                language_code = self._map_language_code(options.language)
                data.add_field('language', language_code)
            
            # Create SSL context that skips certificate verification
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(url, headers=headers, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Extract transcription
                        transcript = result.get('text', '')
                        detected_language = result.get('detected_language', options.language)
                        
                        logger.info("ElevenLabs STT transcription completed", extra={
                            "transcript_length": len(transcript),
                            "detected_language": detected_language
                        })
                        
                        return STTResult(
                            text=transcript,
                            detected_language=detected_language or "auto",
                            confidence=result.get('confidence', 0.9),
                            timestamps=[] if not options.timestamps else self._extract_timestamps(result)
                        )
                    else:
                        error_text = await response.text()
                        raise Exception(f"ElevenLabs STT API error {response.status}: {error_text}")
                        
        except Exception as error:
            logger.error(f"ElevenLabs STT transcription failed: {str(error)}")
            raise Exception(f"ElevenLabs speech-to-text failed: {str(error)}")
    
    def _map_language_code(self, language: str) -> str:
        """Map internal language codes to ElevenLabs format"""
        language_map = {
            "ta": "ta",
            "ta-IN": "ta", 
            "en": "en",
            "en-US": "en",
            "en-IN": "en",
            "auto": "auto"
        }
        return language_map.get(language, "en")
    
    def _extract_timestamps(self, result: Dict[str, Any]) -> List[TimestampInfo]:
        """Extract timestamp information from ElevenLabs response"""
        timestamps = []
        
        # ElevenLabs may provide word-level timestamps in future
        if 'words' in result:
            for word_info in result['words']:
                timestamps.append(TimestampInfo(
                    word=word_info.get('word', ''),
                    start_time=word_info.get('start', 0.0),
                    end_time=word_info.get('end', 0.0),
                    confidence=word_info.get('confidence', 0.9)
                ))
        
        return timestamps
