"""
Vaanga Pesalam - Conversational AI API Routes
Combines STT + LLM + TTS for continuous Tamil/English conversations
"""

import time
import uuid
import logging
import base64
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse, JSONResponse
import io

from app.models.conversation import ConversationRequest, ConversationResponse
from app.adapters.sarvam_stt import SarvamSTTAdapter
from app.adapters.google_stt import GoogleSTTAdapter
from app.adapters.openai_llm import OpenAILLMAdapter
from app.adapters.gemini_llm import GeminiLLMAdapter
from app.adapters.elevenlabs_tts import ElevenLabsTTSAdapter
from app.adapters.google_translate import GoogleTranslateAdapter
from app.models.stt import STTOptions, STTProvider
from app.models.tts import TTSOptions, TTSProvider
from app.middleware.auth import verify_token

logger = logging.getLogger(__name__)
router = APIRouter()

# Session management (in-memory for now)
conversation_sessions = {}


async def get_user_payload_optional(request: Request):
    """Get user payload with optional authentication for testing"""
    skip_auth = request.headers.get("x-skip-auth")
    if skip_auth:
        return {"user_id": "test_user", "skip_auth": True}
    return await verify_token(request)

@router.post("/vaanga-pesalam")
async def vaanga_pesalam_endpoint(
    request: ConversationRequest
):
    """
    Vaanga Pesalam - Conversational AI endpoint
    
    Flow:
    1. STT: Convert user's Tamil/English speech to text
    2. LLM: Generate conversational AI response
    3. TTS: Convert AI response to Tamil/English speech
    4. Return: Audio response for continuous conversation
    """
    start_time = time.time()
    
    try:
        # Extract variables from request
        session_id = request.session_id
        reset_conversation = request.reset_conversation or False
        stt_provider = request.stt_provider or "google"
        llm_provider = request.llm_provider or "gemini"
        tts_provider = request.tts_provider or "elevenlabs"
        voice_speed = getattr(request, 'voice_speed', 1.0)
        audio_data_b64 = request.audio_data
        
        logger.info("Processing Vaanga Pesalam conversation", extra={
            "session_id": session_id,
            "reset_conversation": reset_conversation,
            "stt_provider": stt_provider,
            "has_audio_data": bool(audio_data_b64)
        })
        
        # Generate or use existing session ID
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Get or create conversation session with selected LLM provider
        if session_id not in conversation_sessions or reset_conversation:
            if llm_provider == "gemini":
                conversation_sessions[session_id] = GeminiLLMAdapter()
            else:  # fallback to openai
                conversation_sessions[session_id] = OpenAILLMAdapter()
            if reset_conversation:
                logger.info(f"Reset conversation for session: {session_id}")
        
        # Force Gemini for existing sessions if default has changed
        elif isinstance(conversation_sessions[session_id], OpenAILLMAdapter) and llm_provider == "gemini":
            logger.info(f"Switching session {session_id} from OpenAI to Gemini")
            conversation_sessions[session_id] = GeminiLLMAdapter()
        
        llm_adapter = conversation_sessions[session_id]
        
        # Get audio data from base64
        if audio_data_b64:
            try:
                audio_data = base64.b64decode(audio_data_b64)
                logger.info(f"Processing base64 audio", extra={
                    "base64_length": len(audio_data_b64),
                    "decoded_size": len(audio_data)
                })
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid base64 audio data: {str(e)}")
        else:
            raise HTTPException(status_code=400, detail="No audio data provided")
        
        # Step 1: Transcribe audio using selected STT provider
        stt_provider_name = stt_provider
        stt_options = STTOptions(
            language="auto",
            timestamps=False,
            max_alternatives=1,
            provider=STTProvider(stt_provider_name)
        )
        
        stt_result = None
        actual_provider = stt_provider_name
        
        try:
            if stt_provider_name == "sarvam":
                logger.info("Using Sarvam STT")
                stt_adapter = SarvamSTTAdapter()
                stt_result = await stt_adapter.transcribe(audio_data, stt_options)
            elif stt_provider_name == "elevenlabs":
                logger.info("Using ElevenLabs STT")
                stt_adapter = ElevenLabsSTTAdapter()
                stt_result = await stt_adapter.transcribe(audio_data, stt_options)
            else:  # google
                logger.info("Using Google STT")
                stt_adapter = GoogleSTTAdapter()
                stt_result = await stt_adapter.transcribe(audio_data, stt_options)
        except Exception as stt_error:
            logger.error(f"{stt_provider_name} STT failed: {str(stt_error)}")
            # Fallback to Google STT if primary fails
            if stt_provider_name != "google":
                try:
                    logger.info("Falling back to Google STT")
                    stt_adapter = GoogleSTTAdapter()
                    stt_result = await stt_adapter.transcribe(audio_data, stt_options)
                    actual_provider = "google"
                except Exception as google_error:
                    logger.error(f"Google STT fallback failed: {str(google_error)}")
                    raise HTTPException(status_code=500, detail=f"All STT providers failed: {str(google_error)}")
            else:
                raise HTTPException(status_code=500, detail=f"STT transcription failed: {str(stt_error)}")
        
        user_transcript = stt_result.text.strip()
        user_language = stt_result.detected_language
        
        if not user_transcript:
            raise HTTPException(status_code=400, detail="No speech detected in audio")
        
        logger.info("STT completed", extra={
            "transcript": user_transcript,
            "language": user_language,
            "provider": actual_provider
        })
        
        # Step 2: LLM Conversation
        logger.info("Step 2: Generating AI response")
        
        # Use the session-based LLM adapter (already initialized above)
        # This ensures conversation history is maintained
        
        # Check if this should be a summary/closure (after several exchanges)
        conversation_stats = llm_adapter.get_conversation_summary()
        should_summarize = conversation_stats["message_count"] >= 6  # After 3+ exchanges
        
        ai_response_text = await llm_adapter.chat(
            user_transcript, 
            user_language, 
            should_summarize=should_summarize
        )
        
        # Detect AI response language (simple heuristic)
        ai_response_language = "ta" if any(ord(char) > 2944 and ord(char) < 3071 for char in ai_response_text) else "en"
        
        logger.info("LLM response generated", extra={
            "response_length": len(ai_response_text),
            "response_language": ai_response_language
        })
        
        # Step 3: Text-to-Speech
        logger.info("Step 3: Converting AI response to speech")
        
        # If AI responded in English but user spoke Tamil, translate to Tamil for TTS
        final_tts_text = ai_response_text
        final_tts_language = ai_response_language
        
        if user_language == "ta" and ai_response_language == "en":
            logger.info("Translating AI response to Tamil for TTS")
            translate_adapter = GoogleTranslateAdapter()
            translation_result = await translate_adapter.translate(ai_response_text, "ta", "en")
            final_tts_text = translation_result.text
            final_tts_language = "ta"
        
        # Generate TTS audio
        tts_adapter = ElevenLabsTTSAdapter()
        tts_options = TTSOptions(
            speed=voice_speed,
            provider=TTSProvider(tts_provider)
        )
        
        tts_result = await tts_adapter.synthesize(final_tts_text, final_tts_language, tts_options)
        
        processing_time = time.time() - start_time
        
        # Get conversation stats
        conversation_stats = llm_adapter.get_conversation_summary()
        
        logger.info("Vaanga Pesalam conversation completed", extra={
            "session_id": session_id,
            "user_language": user_language,
            "ai_language": ai_response_language,
            "processing_time": processing_time,
            "audio_size": len(tts_result.audio_data)
        })
        
        # Return audio stream with conversation metadata in headers
        def generate_audio():
            yield tts_result.audio_data
        
        # Encode Tamil text as base64 to avoid header encoding issues
        
        headers = {
            "X-Session-ID": session_id,
            "X-User-Transcript": base64.b64encode(user_transcript.encode('utf-8')).decode('ascii'),
            "X-User-Language": user_language,
            "X-AI-Response": base64.b64encode(ai_response_text.encode('utf-8')).decode('ascii'),
            "X-AI-Language": ai_response_language,
            "X-Processing-Time": str(round(processing_time, 3)),
            "X-Message-Count": str(conversation_stats["message_count"])
        }
        
        return StreamingResponse(
            generate_audio(),
            media_type="audio/mpeg",
            headers=headers
        )
        
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"Vaanga Pesalam conversation failed: {str(error)}")
        
        # Handle ElevenLabs quota exceeded gracefully
        if "quota exceeded" in str(error) or "credits" in str(error):
            # Get the AI response from conversation history
            ai_response = ""
            user_transcript = ""
            
            if llm_adapter and hasattr(llm_adapter, 'conversation_history') and llm_adapter.conversation_history:
                if len(llm_adapter.conversation_history) >= 2:
                    user_transcript = llm_adapter.conversation_history[-2]["content"]
                    ai_response = llm_adapter.conversation_history[-1]["content"]
                elif len(llm_adapter.conversation_history) >= 1:
                    ai_response = llm_adapter.conversation_history[-1]["content"]
            
            return JSONResponse(
                status_code=200,
                content={
                    "message": "Voice synthesis quota exceeded. Please add ElevenLabs credits to continue.",
                    "text_response": ai_response or "Response generated but voice synthesis unavailable."
                },
                headers={
                    "X-Session-ID": session_id,
                    "X-Error-Type": "quota_exceeded",
                    "X-User-Transcript": base64.b64encode(user_transcript.encode()).decode() if user_transcript else "",
                    "X-AI-Response": base64.b64encode(ai_response.encode()).decode() if ai_response else ""
                }
            )
        
        raise HTTPException(status_code=500, detail=f"Conversation processing failed: {str(error)}")


@router.post("/vaanga-pesalam/reset/{session_id}")
async def reset_conversation_endpoint(
    session_id: str,
    user_payload: dict = Depends(verify_token)
):
    """Reset conversation history for a session"""
    try:
        if session_id in conversation_sessions:
            conversation_sessions[session_id].reset_conversation()
            logger.info(f"Conversation reset for session: {session_id}")
            return {"message": "Conversation reset successfully", "session_id": session_id}
        else:
            return {"message": "Session not found", "session_id": session_id}
    except Exception as error:
        logger.error(f"Failed to reset conversation: {str(error)}")
        raise HTTPException(status_code=500, detail="Failed to reset conversation")


@router.get("/vaanga-pesalam/sessions")
async def get_active_sessions(user_payload: dict = Depends(verify_token)):
    """Get list of active conversation sessions"""
    try:
        sessions = []
        for session_id, llm_adapter in conversation_sessions.items():
            stats = llm_adapter.get_conversation_summary()
            sessions.append({
                "session_id": session_id,
                "message_count": stats["message_count"],
                "user_messages": stats["user_messages"],
                "ai_messages": stats["ai_messages"]
            })
        
        return {"active_sessions": len(sessions), "sessions": sessions}
    except Exception as error:
        logger.error(f"Failed to get sessions: {str(error)}")
        raise HTTPException(status_code=500, detail="Failed to get sessions")
