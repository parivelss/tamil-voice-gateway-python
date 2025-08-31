#!/usr/bin/env python3
"""
Comprehensive test for Listen module with real audio generation
"""

import requests
import wave
import numpy as np
import io
import json
from typing import Dict, Any

def create_speech_audio(text: str = "Hello, this is a test", duration: float = 2.0) -> bytes:
    """Create realistic speech-like audio with varying frequencies"""
    sample_rate = 16000
    samples = int(sample_rate * duration)
    
    # Generate speech-like waveform with multiple harmonics
    t = np.linspace(0, duration, samples, False)
    
    # Fundamental frequency (around 150Hz for male voice)
    fundamental = 150
    
    # Create speech-like signal with harmonics and modulation
    signal = (
        0.4 * np.sin(2 * np.pi * fundamental * t) +           # Fundamental
        0.2 * np.sin(2 * np.pi * fundamental * 2 * t) +       # 2nd harmonic
        0.1 * np.sin(2 * np.pi * fundamental * 3 * t) +       # 3rd harmonic
        0.05 * np.sin(2 * np.pi * fundamental * 4 * t)        # 4th harmonic
    )
    
    # Add amplitude modulation to simulate speech patterns
    modulation = 0.5 + 0.5 * np.sin(2 * np.pi * 5 * t)  # 5Hz modulation
    signal = signal * modulation
    
    # Add some noise for realism
    noise = 0.02 * np.random.normal(0, 1, samples)
    signal = signal + noise
    
    # Apply envelope to avoid clicks
    envelope = np.ones_like(signal)
    fade_samples = int(0.05 * sample_rate)  # 50ms fade
    envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
    envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
    signal = signal * envelope
    
    # Convert to 16-bit PCM
    signal = np.clip(signal * 32767, -32768, 32767).astype(np.int16)
    
    # Create WAV file in memory
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(signal.tobytes())
    
    return wav_buffer.getvalue()

def create_silent_audio(duration: float = 1.0) -> bytes:
    """Create silent audio for testing empty speech detection"""
    sample_rate = 16000
    samples = int(sample_rate * duration)
    
    # Create very quiet noise (simulating background)
    signal = 0.001 * np.random.normal(0, 1, samples)
    signal = np.clip(signal * 32767, -32768, 32767).astype(np.int16)
    
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(signal.tobytes())
    
    return wav_buffer.getvalue()

def test_listen_endpoint(audio_data: bytes, test_name: str, stt_provider: str = "google") -> Dict[str, Any]:
    """Test the Listen endpoint with audio data"""
    url = "http://localhost:8006/v1/listen"
    headers = {"x-skip-auth": "true"}
    
    files = {
        'audio': (f'{test_name}.wav', audio_data, 'audio/wav')
    }
    data = {
        'stt_provider': stt_provider,
        'timestamps': 'false'
    }
    
    try:
        print(f"🎤 Testing: {test_name}")
        print(f"   Audio size: {len(audio_data)} bytes")
        print(f"   STT Provider: {stt_provider}")
        
        response = requests.post(url, headers=headers, files=files, data=data, timeout=30)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success!")
            print(f"   Original: '{result.get('original_text', '')}'")
            print(f"   English: '{result.get('english_transcript', '')}'")
            print(f"   Language: {result.get('original_language', 'unknown')}")
            print(f"   Confidence: {result.get('confidence', 0.0)}")
            print(f"   Processing time: {result.get('processing_time_sec', 0.0)}s")
            return result
        else:
            error_detail = response.json().get('detail', 'Unknown error') if response.headers.get('content-type', '').startswith('application/json') else response.text
            print(f"   ❌ Failed: {error_detail}")
            return {"error": error_detail, "status_code": response.status_code}
            
    except requests.exceptions.Timeout:
        print(f"   ⏰ Timeout after 30 seconds")
        return {"error": "Request timeout", "status_code": 408}
    except Exception as e:
        print(f"   💥 Exception: {str(e)}")
        return {"error": str(e), "status_code": 500}

def main():
    """Run comprehensive Listen module tests"""
    print("🚀 Tamil Voice Gateway - Listen Module Comprehensive Test")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        {
            "name": "Speech-like Audio",
            "audio_generator": lambda: create_speech_audio("Hello test audio", 2.0),
            "expected": "Should detect some speech patterns"
        },
        {
            "name": "Short Speech",
            "audio_generator": lambda: create_speech_audio("Quick test", 0.5),
            "expected": "Should handle short audio"
        },
        {
            "name": "Longer Speech",
            "audio_generator": lambda: create_speech_audio("This is a longer test audio", 4.0),
            "expected": "Should handle longer audio"
        },
        {
            "name": "Silent Audio",
            "audio_generator": lambda: create_silent_audio(1.0),
            "expected": "Should return empty transcription"
        },
        {
            "name": "Very Short Audio",
            "audio_generator": lambda: create_speech_audio("Hi", 0.2),
            "expected": "Should handle very short audio"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}/{len(test_cases)}: {test_case['name']}")
        print(f"Expected: {test_case['expected']}")
        print("-" * 40)
        
        try:
            audio_data = test_case['audio_generator']()
            result = test_listen_endpoint(audio_data, test_case['name'])
            results.append({
                "test_name": test_case['name'],
                "result": result,
                "expected": test_case['expected']
            })
        except Exception as e:
            print(f"   💥 Test setup failed: {str(e)}")
            results.append({
                "test_name": test_case['name'],
                "result": {"error": f"Test setup failed: {str(e)}", "status_code": 500},
                "expected": test_case['expected']
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    success_count = 0
    for result in results:
        test_result = result['result']
        if 'error' not in test_result and test_result.get('success', False):
            success_count += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        print(f"{status} - {result['test_name']}")
        if 'error' in test_result:
            print(f"      Error: {test_result['error']}")
    
    print(f"\nResults: {success_count}/{len(results)} tests passed")
    
    if success_count == len(results):
        print("🎉 All tests passed! Listen module is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return results

if __name__ == "__main__":
    main()
