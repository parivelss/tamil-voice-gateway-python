#!/usr/bin/env python3
"""
Simplified test server for UI testing without external dependencies
"""

import asyncio
import base64
import json
import time
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import io

# Mock data models
class ListenResponse(BaseModel):
    success: bool
    english_transcript: str
    original_language: str
    original_text: str
    confidence: float
    processing_time_sec: float
    stt_provider: str
    timestamps: Optional[list] = None

class SpeakRequest(BaseModel):
    english_text: str
    target_language: str
    voice_speed: float = 1.0
    voice_provider: str = "elevenlabs"

class SpeakResponse(BaseModel):
    success: bool
    audio_base64: str
    final_text: str
    final_language: str
    original_text: str
    processing_time_sec: float
    audio_size_bytes: int

# Create FastAPI app
app = FastAPI(title="Tamil Voice Gateway - Test UI", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

async def mock_verify_token(credentials = Depends(security)):
    """Mock JWT verification for testing"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authorization header required")
    return {"userId": "test-user", "email": "test@example.com"}

# Static files
try:
    app.mount("/static", StaticFiles(directory="static", html=True), name="static")
except:
    pass

# Health check
@app.get("/health/")
async def health_check():
    return {
        "ok": True,
        "service": "tamil-voice-gateway-test",
        "version": "2.0.0",
        "timestamp": int(time.time() * 1000)
    }

@app.get("/health/detailed")
async def detailed_health_check():
    return {
        "ok": True,
        "service": "tamil-voice-gateway-test",
        "version": "2.0.0",
        "timestamp": int(time.time() * 1000),
        "status": "healthy",
        "services": {
            "sarvam_stt": "available",
            "google_stt": "available", 
            "google_translate": "available",
            "elevenlabs_tts": "available"
        }
    }

# Mock Listen API
@app.post("/v1/listen", response_model=ListenResponse)
async def listen_endpoint(
    audio: Optional[UploadFile] = File(None),
    audio_base64: Optional[str] = Form(None),
    stt_provider: str = Form("sarvam"),
    timestamps: bool = Form(False),
    user = Depends(mock_verify_token)
):
    """Mock Listen API for UI testing"""
    start_time = time.time()
    
    # Simulate processing delay
    await asyncio.sleep(1)
    
    # Generate varied mock responses based on audio input
    import random
    
    responses = [
        {
            "original_text": "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்?",
            "english_transcript": "Hello, how are you?",
            "original_language": "ta",
            "confidence": 0.94
        },
        {
            "original_text": "இன்று வானிலை எப்படி இருக்கிறது?",
            "english_transcript": "How is the weather today?",
            "original_language": "ta", 
            "confidence": 0.91
        },
        {
            "original_text": "Hello, this is a test of the voice system",
            "english_transcript": "Hello, this is a test of the voice system",
            "original_language": "en",
            "confidence": 0.96
        },
        {
            "original_text": "Thank you for using Tamil Voice Gateway",
            "english_transcript": "Thank you for using Tamil Voice Gateway", 
            "original_language": "en",
            "confidence": 0.93
        },
        {
            "original_text": "வணக்கம், இது ஒரு சோதனை hello mixed language",
            "english_transcript": "Hello, this is a test hello mixed language",
            "original_language": "ta-en",
            "confidence": 0.89
        }
    ]
    
    # Select random response or based on provider
    if stt_provider == "sarvam":
        response = random.choice(responses[:3])  # Prefer Tamil responses for Sarvam
    else:
        response = random.choice(responses[2:])  # Prefer English responses for Google
    
    original_text = response["original_text"]
    english_transcript = response["english_transcript"] 
    original_language = response["original_language"]
    confidence = response["confidence"]
    
    processing_time = time.time() - start_time
    
    return ListenResponse(
        success=True,
        english_transcript=english_transcript,
        original_language=original_language,
        original_text=original_text,
        confidence=confidence,
        processing_time_sec=round(processing_time, 3),
        stt_provider=stt_provider,
        timestamps=None
    )

# Mock Speak API
@app.post("/v1/speak")
async def speak_endpoint(
    request: SpeakRequest,
    user = Depends(mock_verify_token)
):
    """Mock Speak API for UI testing"""
    start_time = time.time()
    
    # Simulate processing delay
    await asyncio.sleep(1.5)
    
    # Mock translation
    if request.target_language == "ta":
        final_text = "வணக்கம், இது தமிழ் குரல் நுழைவாயிலின் சோதனை"
        final_language = "ta"
    else:
        final_text = request.english_text
        final_language = "en"
    
    # Generate actual playable audio data (simple WAV format)
    # Create a simple WAV header + tone for testing
    import struct
    import math
    
    # WAV file parameters
    sample_rate = 22050
    duration = 2.0  # 2 seconds
    frequency = 440  # A4 note
    
    # Generate sine wave
    samples = []
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        sample = int(32767 * math.sin(2 * math.pi * frequency * t) * 0.3)  # 30% volume
        samples.append(struct.pack('<h', sample))
    
    # WAV header
    wav_header = struct.pack('<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        36 + len(samples) * 2,  # File size
        b'WAVE',
        b'fmt ',
        16,  # PCM format chunk size
        1,   # PCM format
        1,   # Mono
        sample_rate,
        sample_rate * 2,  # Byte rate
        2,   # Block align
        16,  # Bits per sample
        b'data',
        len(samples) * 2  # Data size
    )
    
    mock_audio = wav_header + b''.join(samples)
    
    processing_time = time.time() - start_time
    
    return StreamingResponse(
        io.BytesIO(mock_audio),
        media_type="audio/wav",
        headers={
            "X-Processing-Time": str(round(processing_time, 3)),
            "X-Final-Language": final_language,
            "X-Original-Text-Length": str(len(request.english_text)),
            "X-Final-Text-Length": str(len(final_text))
        }
    )

# Mock Speak Preview API
@app.post("/v1/speak/preview", response_model=SpeakResponse)
async def speak_preview_endpoint(
    request: SpeakRequest,
    user = Depends(mock_verify_token)
):
    """Mock Speak Preview API for UI testing"""
    start_time = time.time()
    
    # Simulate processing delay
    await asyncio.sleep(1)
    
    # Mock translation
    if request.target_language == "ta":
        final_text = "வணக்கம், இது தமிழ் குரல் நுழைவாயிலின் சோதனை"
        final_language = "ta"
    else:
        final_text = request.english_text
        final_language = "en"
    
    # Generate mock audio data
    mock_audio = f"MOCK_AUDIO_DATA_{final_text[:20]}".encode('utf-8')
    mock_audio += b'\x00' * 1000
    
    processing_time = time.time() - start_time
    
    return SpeakResponse(
        success=True,
        audio_base64=base64.b64encode(mock_audio).decode('utf-8'),
        final_text=final_text,
        final_language=final_language,
        original_text=request.english_text,
        processing_time_sec=round(processing_time, 3),
        audio_size_bytes=len(mock_audio)
    )

if __name__ == "__main__":
    import uvicorn
    print("🎙️ Tamil Voice Gateway - Test UI Server")
    print("=" * 50)
    print("🌐 Server starting at: http://localhost:8003")
    print("📱 Web UI: http://localhost:8003/static/")
    print("📚 API Docs: http://localhost:8003/docs")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")
