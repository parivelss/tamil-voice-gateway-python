"""
ElevenLabs Text-to-Speech Adapter
"""

import httpx
import logging
from typing import Optional, Dict, Any, List
import base64
import re
import io

from app.core.config import settings
from app.models.tts import TTSResult, TTSOptions
from app.adapters.base import TTSAdapter

logger = logging.getLogger(__name__)


class ElevenLabsTTSAdapter(TTSAdapter):
    """ElevenLabs TTS adapter"""
    
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY is required for ElevenLabs TTS adapter")
    
    async def synthesize(self, text: str, language: str, options: TTSOptions) -> TTSResult:
        """
        Synthesize text to speech using ElevenLabs
        
        Args:
            text: Text to synthesize
            language: Target language
            options: TTS options
            
        Returns:
            TTSResult with audio data
        """
        try:
            logger.info("Starting ElevenLabs TTS synthesis", extra={
                "text_length": len(text),
                "language": language,
                "speed": options.speed
            })
            
            # Handle long texts by chunking
            if len(text) > 2500:  # ElevenLabs actual limit is ~5000 chars, use 2500 for safety
                return await self._synthesize_long_text(text, language, options)
            
            # Get voice ID for language
            voice_id = options.voice_id or self._get_default_voice_id(language)
            model = options.model or settings.ELEVENLABS_TTS_MODEL
            
            # Prepare request
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": text,
                "model_id": model,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True,
                }
            }
            
            # Add speed control if supported
            if options.speed != 1.0:
                data["voice_settings"]["speed"] = options.speed
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=data, headers=headers)
                
                if not response.is_success:
                    error_text = response.text
                    logger.error(f"ElevenLabs TTS API error: {response.status_code} - {error_text}")
                    raise Exception(f"ElevenLabs TTS API error: {response.status_code} - {error_text}")
                
                audio_data = response.content
                
                if not audio_data:
                    raise Exception("No audio data returned from ElevenLabs TTS")
                
                result = TTSResult(
                    audio_data=audio_data,
                    audio_format="mp3",
                    duration_sec=None,  # ElevenLabs doesn't provide duration
                    provider="elevenlabs"
                )
                
                logger.info("ElevenLabs TTS synthesis completed", extra={
                    "audio_size": len(audio_data),
                    "voice_id": voice_id,
                    "model": model
                })
                
                return result
                
        except Exception as error:
            logger.error(f"ElevenLabs TTS synthesis failed: {str(error)}")
            
            # Check if it's a quota exceeded error
            if "quota_exceeded" in str(error) or "credits" in str(error):
                logger.warning("ElevenLabs quota exceeded, returning text response instead of audio")
                # Return a minimal audio response or raise a specific quota error
                raise Exception("ElevenLabs quota exceeded - please add credits to continue voice synthesis")
            
            raise Exception(f"ElevenLabs text-to-speech failed: {str(error)}")
    
    def _get_default_voice_id(self, language: str) -> str:
        """Get default voice ID for language"""
        if language == "ta" and settings.ELEVENLABS_VOICE_ID_TA:
            return settings.ELEVENLABS_VOICE_ID_TA
        elif language == "en" and settings.ELEVENLABS_VOICE_ID_EN:
            return settings.ELEVENLABS_VOICE_ID_EN
        
        # Fallback voice IDs
        voice_map = {
            "ta": "eh0hAHy3N3C9DE0uyHHD",  # Srivi (Tamil)
            "en": "EXAVITQu4vr4xnSDxMaL"   # Sarah (English)
        }
        
        return voice_map.get(language, voice_map["en"])
    
    async def _synthesize_long_text(self, text: str, language: str, options: TTSOptions) -> TTSResult:
        """
        Synthesize long text by chunking it into smaller pieces
        """
        logger.info(f"Chunking long text of {len(text)} characters")
        
        # Split text into chunks at sentence boundaries
        chunks = self._split_text_into_chunks(text, max_chunk_size=2000)
        audio_chunks = []
        
        for i, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {i+1}/{len(chunks)} ({len(chunk)} chars)")
            
            # Synthesize each chunk
            chunk_result = await self._synthesize_single_chunk(chunk, language, options)
            audio_chunks.append(chunk_result.audio_data)
        
        # Concatenate all audio chunks
        combined_audio = self._concatenate_audio_chunks(audio_chunks)
        
        result = TTSResult(
            audio_data=combined_audio,
            audio_format="mp3",
            duration_sec=None,
            provider="elevenlabs"
        )
        
        logger.info(f"Long text synthesis completed: {len(chunks)} chunks, {len(combined_audio)} bytes")
        return result
    
    def _split_text_into_chunks(self, text: str, max_chunk_size: int = 2000) -> List[str]:
        """
        Split text into chunks at sentence boundaries
        """
        # First try to split at sentence endings
        sentences = re.split(r'[.!?]+\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # If adding this sentence would exceed the limit, start a new chunk
            if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                if current_chunk:
                    current_chunk += ". " + sentence
                else:
                    current_chunk = sentence
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # If any chunk is still too long, split it further
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= max_chunk_size:
                final_chunks.append(chunk)
            else:
                # Split by words if sentence splitting wasn't enough
                words = chunk.split()
                current_word_chunk = ""
                
                for word in words:
                    if len(current_word_chunk) + len(word) + 1 > max_chunk_size and current_word_chunk:
                        final_chunks.append(current_word_chunk.strip())
                        current_word_chunk = word
                    else:
                        if current_word_chunk:
                            current_word_chunk += " " + word
                        else:
                            current_word_chunk = word
                
                if current_word_chunk:
                    final_chunks.append(current_word_chunk.strip())
        
        return final_chunks
    
    async def _synthesize_single_chunk(self, text: str, language: str, options: TTSOptions) -> TTSResult:
        """
        Synthesize a single text chunk
        """
        voice_id = options.voice_id or self._get_default_voice_id(language)
        model = options.model or settings.ELEVENLABS_TTS_MODEL
        
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": model,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True,
            }
        }
        
        if options.speed != 1.0:
            data["voice_settings"]["speed"] = options.speed
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=data, headers=headers)
            
            if not response.is_success:
                error_text = response.text
                logger.error(f"ElevenLabs TTS API error: {response.status_code} - {error_text}")
                raise Exception(f"ElevenLabs TTS API error: {response.status_code} - {error_text}")
            
            audio_data = response.content
            
            if not audio_data:
                raise Exception("No audio data returned from ElevenLabs TTS")
            
            return TTSResult(
                audio_data=audio_data,
                audio_format="mp3",
                duration_sec=None,
                provider="elevenlabs"
            )
    
    def _concatenate_audio_chunks(self, audio_chunks: List[bytes]) -> bytes:
        """
        Concatenate multiple MP3 audio chunks
        Note: This is a simple concatenation. For better quality, 
        consider using audio processing libraries like pydub
        """
        if not audio_chunks:
            return b""
        
        if len(audio_chunks) == 1:
            return audio_chunks[0]
        
        # Simple concatenation - works for most cases with MP3
        combined = b"".join(audio_chunks)
        return combined
