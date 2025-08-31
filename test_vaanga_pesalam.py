#!/usr/bin/env python3
"""
Test Vaanga Pesalam conversational AI module
"""

import requests
import json
import time

def test_vaanga_pesalam():
    """Test the Vaanga Pesalam conversational AI endpoint"""
    url = "http://localhost:8006/v1/vaanga-pesalam"
    headers = {
        "Content-Type": "application/json",
        "x-skip-auth": "true"
    }
    
    # Test conversation request - Create proper WAV audio
    import base64
    import wave
    import numpy as np
    import io
    
    # Create minimal valid WAV audio
    sample_rate = 16000
    duration = 1.0
    samples = int(sample_rate * duration)
    
    # Generate simple sine wave
    t = np.linspace(0, duration, samples, False)
    signal = 0.3 * np.sin(2 * np.pi * 440 * t)  # 440Hz tone
    signal = np.clip(signal * 32767, -32768, 32767).astype(np.int16)
    
    # Create WAV file in memory
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(signal.tobytes())
    
    test_audio = wav_buffer.getvalue()
    audio_b64 = base64.b64encode(test_audio).decode('utf-8')
    
    data = {
        "audio_data": audio_b64,
        "llm_provider": "gemini",
        "session_id": "test_session_123"
    }
    
    try:
        print("🤖 Testing Vaanga Pesalam Conversational AI")
        print("=" * 50)
        print(f"Audio Data: {len(audio_b64)} chars (base64)")
        print(f"LLM Provider: {data['llm_provider']}")
        print(f"Session ID: {data['session_id']}")
        print("\n📤 Sending request...")
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Response: {result.get('response', '')}")
            print(f"Session ID: {result.get('session_id', '')}")
            print(f"Processing time: {result.get('processing_time_sec', 0.0)}s")
            
            # Check if response contains Tamil/medical content
            response_text = result.get('response', '')
            if any(word in response_text.lower() for word in ['வணக்கம்', 'headache', 'pain', 'symptoms']):
                print("🎯 Response contains expected medical/Tamil content!")
            else:
                print("⚠️  Response may not contain expected content")
                
            return result
        else:
            try:
                error_detail = response.json().get('detail', 'Unknown error')
            except:
                error_detail = response.text
            print(f"❌ Failed: {error_detail}")
            return {"error": error_detail, "status_code": response.status_code}
            
    except Exception as e:
        print(f"💥 Exception: {str(e)}")
        return {"error": str(e), "status_code": 500}

def test_conversation_flow():
    """Test a full conversation flow"""
    print("\n🔄 Testing Conversation Flow")
    print("=" * 50)
    
    session_id = f"test_flow_{int(time.time())}"
    
    # Conversation messages
    messages = [
        "Hi, I have been having fever since yesterday",
        "It's around 101°F and I also have body ache",
        "No, I haven't taken any medicine yet"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n💬 Message {i}: {message}")
        
        # Create proper WAV audio for each message
        import base64
        import wave
        import numpy as np
        import io
        
        # Create minimal valid WAV audio
        sample_rate = 16000
        duration = 0.5
        samples = int(sample_rate * duration)
        
        # Generate simple sine wave with different frequency for each message
        frequency = 440 + (i * 100)  # Different frequency for each message
        t = np.linspace(0, duration, samples, False)
        signal = 0.3 * np.sin(2 * np.pi * frequency * t)
        signal = np.clip(signal * 32767, -32768, 32767).astype(np.int16)
        
        # Create WAV file in memory
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(signal.tobytes())
        
        test_audio = wav_buffer.getvalue()
        audio_b64 = base64.b64encode(test_audio).decode('utf-8')
        
        data = {
            "audio_data": audio_b64,
            "llm_provider": "gemini", 
            "session_id": session_id
        }
        
        try:
            response = requests.post(
                "http://localhost:8006/v1/vaanga-pesalam",
                headers={"Content-Type": "application/json", "x-skip-auth": "true"},
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', '')
                print(f"🤖 AI Response: {ai_response[:200]}{'...' if len(ai_response) > 200 else ''}")
            else:
                print(f"❌ Failed: {response.status_code}")
                break
                
        except Exception as e:
            print(f"💥 Error: {str(e)}")
            break
    
    print("\n✅ Conversation flow test completed")

if __name__ == "__main__":
    # Test single message
    result = test_vaanga_pesalam()
    
    # Test conversation flow if single message worked
    if 'error' not in result:
        test_conversation_flow()
    else:
        print("\n⚠️  Skipping conversation flow test due to single message failure")
    
    print("\n🎉 Vaanga Pesalam testing completed!")
