#!/usr/bin/env python3
"""
Test Tamil Voice Gateway with real audio recording
"""

import asyncio
import base64
import json
import requests
import pyaudio
import wave
import tempfile
import os

def record_audio(duration=3, sample_rate=16000):
    """Record audio from microphone"""
    print(f"Recording for {duration} seconds...")
    
    chunk = 1024
    format = pyaudio.paInt16
    channels = 1
    
    audio = pyaudio.PyAudio()
    
    stream = audio.open(format=format,
                       channels=channels,
                       rate=sample_rate,
                       input=True,
                       frames_per_buffer=chunk)
    
    frames = []
    
    for i in range(0, int(sample_rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)
    
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # Save to temporary WAV file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        wf = wave.open(temp_file.name, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(format))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        # Read back as bytes
        with open(temp_file.name, 'rb') as f:
            audio_data = f.read()
        
        os.unlink(temp_file.name)
        return audio_data

def test_speak_module():
    """Test Speak module"""
    print("\n=== Testing Speak Module ===")
    
    url = "http://localhost:8005/v1/speak"
    headers = {
        "Content-Type": "application/json",
        "x-skip-auth": "true"
    }
    
    payload = {
        "english_text": "Hello, this is a test of the Tamil Voice Gateway",
        "target_language": "en",
        "voice_speed": 1.0,
        "voice_provider": "elevenlabs"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Audio size: {len(response.content)} bytes")
            print("✅ Speak module working!")
            
            # Save audio file
            with open("test_output.mp3", "wb") as f:
                f.write(response.content)
            print("Audio saved as test_output.mp3")
            
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_listen_module():
    """Test Listen module with real audio"""
    print("\n=== Testing Listen Module ===")
    
    try:
        # Record audio
        audio_data = record_audio(duration=3)
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        
        url = "http://localhost:8005/v1/listen"
        headers = {
            "Content-Type": "application/json",
            "x-skip-auth": "true"
        }
        
        payload = {
            "audio_base64": audio_b64,
            "stt_provider": "google",
            "timestamps": False
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Transcription: {result.get('english_transcript', 'N/A')}")
            print(f"Original: {result.get('original_text', 'N/A')}")
            print(f"Language: {result.get('original_language', 'N/A')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_vaanga_pesalam():
    """Test Vaanga Pesalam with real audio"""
    print("\n=== Testing Vaanga Pesalam ===")
    
    try:
        # Record audio
        audio_data = record_audio(duration=3)
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        
        url = "http://localhost:8005/v1/vaanga-pesalam"
        headers = {
            "Content-Type": "application/json",
            "x-skip-auth": "true"
        }
        
        payload = {
            "session_id": "test_session",
            "audio_data": audio_b64,
            "stt_provider": "google",
            "llm_provider": "openai",
            "tts_provider": "elevenlabs",
            "reset_conversation": False
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Audio response size: {len(response.content)} bytes")
            
            # Check headers for conversation data
            user_transcript = response.headers.get('X-User-Transcript')
            ai_response = response.headers.get('X-AI-Response')
            
            if user_transcript:
                user_text = base64.b64decode(user_transcript).decode('utf-8')
                print(f"User said: {user_text}")
            
            if ai_response:
                ai_text = base64.b64decode(ai_response).decode('utf-8')
                print(f"AI replied: {ai_text}")
            
            # Save audio response
            with open("vaanga_response.mp3", "wb") as f:
                f.write(response.content)
            print("AI response saved as vaanga_response.mp3")
            print("✅ Vaanga Pesalam working!")
            
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("Tamil Voice Gateway Real Audio Test")
    print("=" * 40)
    
    # Test all modules
    test_speak_module()
    test_listen_module() 
    test_vaanga_pesalam()
    
    print("\n" + "=" * 40)
    print("Testing complete!")
