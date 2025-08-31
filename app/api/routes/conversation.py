"""
Real-time conversation API routes
"""

import logging
import time
import base64
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import StreamingResponse
import io

from app.models.stt import ListenRequest, ListenResponse, STTOptions, STTProvider
from app.models.tts import SpeakRequest, SpeakResponse, TTSOptions
from app.adapters.sarvam_stt import SarvamSTTAdapter
from app.adapters.google_stt import GoogleSTTAdapter
from app.adapters.elevenlabs_stt import ElevenLabsSTTAdapter
from app.adapters.elevenlabs_tts import ElevenLabsTTSAdapter
from app.adapters.google_translate import GoogleTranslateAdapter
from app.adapters.gemini_translate import GeminiTranslateAdapter
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/listen", response_model=ListenResponse)
async def listen_endpoint(
    audio: Optional[UploadFile] = File(None),
    audio_base64: Optional[str] = Form(None),
    stt_provider: STTProvider = Form(STTProvider.SARVAM),
    timestamps: bool = Form(False)
):
    """
    Listen API - Voice to English transcript with language detection
    
    Process flow (as per specification):
    1. Input: Voice recording (any language/mixed languages)
    2. Process: 
       - Detects language from audio
       - STT transcribes in detected language (supports Tamil/English mix)
       - Translates transcript to English
    3. Output: English transcript + detected language
    """
    start_time = time.time()
    
    try:
        logger.info("Processing listen request", extra={
            "stt_provider": stt_provider.value,
            "timestamps": timestamps,
            "has_file": bool(audio),
            "has_base64": bool(audio_base64)
        })
        
        # Get audio data
        if audio:
            audio_data = await audio.read()
            logger.info(f"Processing uploaded audio file", extra={
                "audio_filename": audio.filename,
                "audio_size": len(audio_data),
                "content_type": audio.content_type
            })
        elif audio_base64:
            try:
                audio_data = base64.b64decode(audio_base64)
                logger.info(f"Processing base64 audio", extra={
                    "base64_length": len(audio_base64),
                    "decoded_size": len(audio_data)
                })
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid base64 audio data: {str(e)}")
        else:
            raise HTTPException(status_code=400, detail="Either audio file or audio_base64 is required")
        
        # Validate audio size (30 second limit approximation)
        if len(audio_data) > 5 * 1024 * 1024:  # 5MB limit
            raise HTTPException(status_code=400, detail="Audio file too large (max 5MB)")
        
        # Initialize adapters
        translate_adapter = GoogleTranslateAdapter()
        
        # Step 1: Detect language first
        logger.info("Step 1: Detecting language from audio")
        detected_language = None
        
        # Use a quick STT call to detect language
        try:
            if stt_provider == STTProvider.SARVAM:
                stt_adapter = SarvamSTTAdapter()
                # Sarvam automatically detects language, so we do a quick transcribe
                stt_options = STTOptions(language="auto", timestamps=False, provider=stt_provider)
                quick_result = await stt_adapter.transcribe(audio_data, stt_options)
                detected_language = quick_result.detected_language
            else:
                # For Google, we can use language detection or try auto-detect
                translate_adapter = GoogleTranslateAdapter()
                # First try a quick STT to get some text for language detection
                stt_adapter = GoogleSTTAdapter()
                stt_options = STTOptions(language="auto", timestamps=False, provider=stt_provider)
                quick_result = await stt_adapter.transcribe(audio_data, stt_options)
                detected_language = quick_result.detected_language or await translate_adapter.detect_language(quick_result.text)
                
            logger.info(f"Language detected: {detected_language}")
            
        except Exception as detection_error:
            logger.warning(f"Language detection failed, defaulting to auto: {str(detection_error)}")
            detected_language = "auto"
        
        # Step 2: STT with detected language
        
        stt_options = STTOptions(
            language=detected_language,
            timestamps=timestamps,
            provider=stt_provider
        )
        
        stt_result = None
        actual_provider = stt_provider.value
        
        try:
            if stt_provider == STTProvider.SARVAM:
                try:
                    logger.info("Using Sarvam STT as primary provider")
                    stt_adapter = SarvamSTTAdapter()
                    stt_result = await stt_adapter.transcribe(audio_data, stt_options)
                    logger.info("Sarvam STT successful")
                except Exception as sarvam_error:
                    logger.warning(f"Sarvam STT failed: {str(sarvam_error)}")
                    logger.info("Falling back to Google STT")
                    stt_adapter = GoogleSTTAdapter()
                    stt_result = await stt_adapter.transcribe(audio_data, stt_options)
                    logger.info("Google STT fallback successful")
            elif stt_provider == STTProvider.ELEVENLABS:
                logger.info("Using ElevenLabs STT as primary provider")
                stt_adapter = ElevenLabsSTTAdapter()
                stt_result = await stt_adapter.transcribe(audio_data, stt_options)
            else:
                # Use Google STT directly
                logger.info("Using Google STT as primary provider")
                stt_adapter = GoogleSTTAdapter()
                stt_result = await stt_adapter.transcribe(audio_data, stt_options)
        except Exception as stt_error:
            logger.warning(f"Primary STT failed: {str(stt_error)}")
            
            # Fallback to Google STT if Sarvam failed
            if stt_provider == STTProvider.SARVAM:
                try:
                    logger.info("Falling back to Google STT")
                    stt_adapter = GoogleSTTAdapter()
                    stt_options.provider = STTProvider.GOOGLE
                    stt_result = await stt_adapter.transcribe(audio_data, stt_options)
                    actual_provider = "google_fallback"
                    logger.info("Google STT fallback successful", extra={
                        "confidence": stt_result.confidence
                    })
                except Exception as fallback_error:
                    logger.error(f"STT fallback also failed: {str(fallback_error)}")
                    raise HTTPException(status_code=500, detail=f"Speech recognition failed: {str(fallback_error)}")
            else:
                raise HTTPException(status_code=500, detail=f"Speech recognition failed: {str(stt_error)}")
        
        # Step 3: Preparing transcripts
        logger.info("Step 3: Preparing transcripts")
        english_transcript = stt_result.text
        if stt_result.text and stt_result.detected_language and stt_result.detected_language not in ["en", "en-US", "en-IN"]:
            logger.info("Step 3: Translating to English")
            english_transcript = await translate_adapter.translate_to_english(
                stt_result.text,
                source_language=stt_result.detected_language
            )
        elif not stt_result.text:
            logger.info("No speech detected, skipping translation")
            english_transcript = ""
        else:
            logger.info("Text is already in English, no translation needed")
        
        processing_time = time.time() - start_time
        
        response = ListenResponse(
            success=True,
            english_transcript=english_transcript,
            original_language=stt_result.detected_language or "auto",
            original_text=stt_result.text,
            confidence=stt_result.confidence,
            processing_time_sec=round(processing_time, 3),
            stt_provider=actual_provider,
            timestamps=stt_result.timestamps if timestamps else None
        )
        
        logger.info("Listen request completed", extra={
            "original_language": stt_result.detected_language or "auto",
            "english_length": len(english_transcript),
            "processing_time": processing_time,
            "provider": actual_provider
        })
        
        return response
        
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"Listen request failed: {str(error)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/speak")
async def speak_endpoint(request: SpeakRequest):
    """
    Speak API - English text to target language audio
    
    Process flow (as per specification):
    1. Input: English text + target language
    2. Process: 
       - Translates English text to target language
       - TTS generates audio in target language
    3. Output: Audio recording in target language
    """
    start_time = time.time()
    
    try:
        logger.info("Processing speak request", extra={
            "text_length": len(request.english_text),
            "target_language": request.target_language,
            "voice_provider": request.voice_provider.value,
            "voice_speed": request.voice_speed
        })
        
        # Initialize adapters
        tts_adapter = ElevenLabsTTSAdapter()
        
        # Step 1: Always translate English text to target language (as per spec)
        logger.info(f"Step 1: Translating English to target language: {request.target_language}")
        
        if request.target_language == "en":
            # Target is English, no translation needed
            final_text = request.english_text
            actual_language = "en"
            logger.info("Target language is English, no translation needed")
        elif request.target_language == "ta":
            # Use Gemini for colloquial Tamil translation
            logger.info("Using Gemini for colloquial Tamil translation")
            gemini_translate_adapter = GeminiTranslateAdapter()
            final_text = await gemini_translate_adapter.translate_to_colloquial_tamil(request.english_text)
            actual_language = "ta"
        else:
            # Fallback to Google Translate for other languages
            logger.info(f"Using Google Translate for {request.target_language}")
            translate_adapter = GoogleTranslateAdapter()
            translation_result = await translate_adapter.translate(
                request.english_text, request.target_language, "en"
            )
            final_text = translation_result.text
            actual_language = request.target_language
            
            logger.info("Translation completed", extra={
                "target_language": request.target_language,
                "original_length": len(request.english_text),
                "translated_length": len(final_text)
            })
        
        # Generate TTS audio
        tts_options = TTSOptions(
            speed=request.voice_speed,
            provider=request.voice_provider
        )
        
        tts_result = await tts_adapter.synthesize(final_text, actual_language, tts_options)
        
        processing_time = time.time() - start_time
        
        logger.info("Speak request completed", extra={
            "audio_size": len(tts_result.audio_data),
            "final_language": actual_language,
            "processing_time": processing_time
        })
        
        # Return audio stream
        return StreamingResponse(
            io.BytesIO(tts_result.audio_data),
            media_type="audio/mpeg",
            headers={
                "X-Processing-Time": str(round(processing_time, 3)),
                "X-Final-Language": actual_language,
                "X-Original-Text-Length": str(len(request.english_text)),
                "X-Final-Text-Length": str(len(final_text))
            }
        )
        
    except Exception as error:
        logger.error(f"Speak request failed: {str(error)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/speak/preview", response_model=SpeakResponse)
async def speak_preview_endpoint(request: SpeakRequest):
    """
    Speak Preview API - Returns JSON with base64 audio
    Useful for testing and debugging
    """
    start_time = time.time()
    
    try:
        logger.info("Processing speak preview request", extra={
            "text_length": len(request.english_text),
            "target_language": request.target_language
        })
        
        # Initialize adapters
        translate_adapter = GoogleTranslateAdapter()
        tts_adapter = ElevenLabsTTSAdapter()
        
        final_text = request.english_text
        actual_language = "en"
        
        # Translate if needed
        if request.target_language == "ta":
            # Use Gemini for colloquial Tamil translation
            gemini_translate_adapter = GeminiTranslateAdapter()
            final_text = await gemini_translate_adapter.translate_to_colloquial_tamil(request.english_text)
            actual_language = "ta"
        
        # Generate TTS audio
        tts_options = TTSOptions(
            speed=request.voice_speed,
            provider=request.voice_provider
        )
        
        tts_result = await tts_adapter.synthesize(final_text, actual_language, tts_options)
        
        processing_time = time.time() - start_time
        
        response = SpeakResponse(
            success=True,
            audio_base64=base64.b64encode(tts_result.audio_data).decode('utf-8'),
            final_text=final_text,
            final_language=actual_language,
            original_text=request.english_text,
            processing_time_sec=round(processing_time, 3),
            audio_size_bytes=len(tts_result.audio_data)
        )
        
        logger.info("Speak preview completed", extra={
            "audio_size": len(tts_result.audio_data),
            "final_language": actual_language,
            "processing_time": processing_time
        })
        
        return response
        
    except Exception as error:
        logger.error(f"Speak preview failed: {str(error)}")
        raise HTTPException(status_code=500, detail="Internal server error")
