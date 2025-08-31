#!/usr/bin/env python3
"""
Test Listen module with proper audio data
"""

import requests
import base64
import io
import wave

def create_minimal_wav():
    """Create minimal valid WAV file"""
    # Create a 1-second silence WAV file
    sample_rate = 16000
    duration = 1  # 1 second
    samples = sample_rate * duration
    
    # Create WAV file in memory
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Write silence (zeros)
        silence = b'\x00\x00' * samples
        wav_file.writeframes(silence)
    
    wav_buffer.seek(0)
    return wav_buffer.getvalue()

def test_listen_module():
    """Test Listen module with valid audio"""
    print("🎤 Testing Listen Module")
    print("=" * 50)
    
    # Create valid WAV audio
    audio_data = create_minimal_wav()
    print(f"Created WAV audio: {len(audio_data)} bytes")
    
    url = "http://localhost:8006/v1/listen"
    headers = {"x-skip-auth": "true"}
    
    # Test with file upload
    files = {
        'audio': ('test.wav', audio_data, 'audio/wav')
    }
    data = {
        'stt_provider': 'google',
        'timestamps': 'false'
    }
    
    try:
        print("\n📤 Sending request...")
        response = requests.post(url, headers=headers, files=files, data=data, timeout=30)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Listen module working!")
            print(f"Original text: {result.get('original_text', 'N/A')}")
            print(f"English text: {result.get('english_transcript', 'N/A')}")
            print(f"Language: {result.get('original_language', 'N/A')}")
        else:
            print(f"\n❌ Listen module failed: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Request failed: {str(e)}")

if __name__ == "__main__":
    test_listen_module()
