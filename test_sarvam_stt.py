#!/usr/bin/env python3
"""
Test Listen module with Sarvam AI STT provider
"""

import requests
import wave
import numpy as np
import io
import json

def create_realistic_speech_audio(duration: float = 3.0) -> bytes:
    """Create more realistic speech audio with formants and speech patterns"""
    sample_rate = 16000
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, False)
    
    # Create speech-like signal with formants (vowel-like sounds)
    # Formant frequencies for vowel sounds
    f1, f2, f3 = 800, 1200, 2500  # Approximate formants for /a/ sound
    
    # Generate formant-based signal
    signal = (
        0.3 * np.sin(2 * np.pi * f1 * t) +     # First formant
        0.2 * np.sin(2 * np.pi * f2 * t) +     # Second formant  
        0.1 * np.sin(2 * np.pi * f3 * t)       # Third formant
    )
    
    # Add pitch variation (prosody)
    pitch_base = 120  # Base pitch in Hz
    pitch_variation = 20 * np.sin(2 * np.pi * 0.5 * t)  # Slow pitch changes
    pitch = pitch_base + pitch_variation
    
    # Modulate with pitch
    pitch_signal = 0.4 * np.sin(2 * np.pi * pitch * t)
    signal = signal + pitch_signal
    
    # Add speech-like amplitude modulation (syllables)
    syllable_rate = 4  # 4 syllables per second
    amplitude_mod = 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * syllable_rate * t))
    signal = signal * amplitude_mod
    
    # Add consonant-like noise bursts
    for i in range(int(duration * 2)):  # 2 bursts per second
        burst_start = int(i * sample_rate / 2)
        burst_end = min(burst_start + int(0.05 * sample_rate), samples)
        if burst_end < samples:
            noise_burst = 0.1 * np.random.normal(0, 1, burst_end - burst_start)
            signal[burst_start:burst_end] += noise_burst
    
    # Apply realistic envelope
    envelope = np.ones_like(signal)
    fade_samples = int(0.1 * sample_rate)
    envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
    envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
    signal = signal * envelope
    
    # Add background noise
    background_noise = 0.01 * np.random.normal(0, 1, samples)
    signal = signal + background_noise
    
    # Normalize and convert to 16-bit PCM
    signal = signal / np.max(np.abs(signal)) * 0.8  # Prevent clipping
    signal = np.clip(signal * 32767, -32768, 32767).astype(np.int16)
    
    # Create WAV file
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(signal.tobytes())
    
    return wav_buffer.getvalue()

def test_with_provider(audio_data: bytes, provider: str, test_name: str):
    """Test Listen endpoint with specific STT provider"""
    url = "http://localhost:8006/v1/listen"
    headers = {"x-skip-auth": "true"}
    
    files = {
        'audio': (f'{test_name}_{provider}.wav', audio_data, 'audio/wav')
    }
    data = {
        'stt_provider': provider,
        'timestamps': 'false'
    }
    
    try:
        print(f"\n🎤 Testing with {provider.upper()} STT")
        print(f"   Test: {test_name}")
        print(f"   Audio size: {len(audio_data)} bytes")
        
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
            
            # Check if we got actual transcription
            has_text = bool(result.get('original_text', '').strip() or result.get('english_transcript', '').strip())
            if has_text:
                print(f"   🎯 DETECTED SPEECH!")
            else:
                print(f"   🔇 No speech detected")
            
            return result
        else:
            try:
                error_detail = response.json().get('detail', 'Unknown error')
            except:
                error_detail = response.text
            print(f"   ❌ Failed: {error_detail}")
            return {"error": error_detail, "status_code": response.status_code}
            
    except Exception as e:
        print(f"   💥 Exception: {str(e)}")
        return {"error": str(e), "status_code": 500}

def main():
    """Test Listen module with both STT providers"""
    print("🚀 Tamil Voice Gateway - STT Provider Comparison Test")
    print("=" * 60)
    
    # Generate realistic speech audio
    print("🎵 Generating realistic speech-like audio...")
    audio_data = create_realistic_speech_audio(3.0)
    print(f"Generated {len(audio_data)} bytes of audio")
    
    # Test with both providers
    providers = ["google", "sarvam"]
    results = {}
    
    for provider in providers:
        result = test_with_provider(audio_data, provider, "realistic_speech")
        results[provider] = result
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 COMPARISON SUMMARY")
    print("=" * 60)
    
    for provider in providers:
        result = results[provider]
        if 'error' not in result:
            has_text = bool(result.get('original_text', '').strip() or result.get('english_transcript', '').strip())
            status = "🎯 DETECTED SPEECH" if has_text else "🔇 No speech detected"
            confidence = result.get('confidence', 0.0)
            processing_time = result.get('processing_time_sec', 0.0)
            print(f"{provider.upper()}: {status} (confidence: {confidence:.2f}, time: {processing_time:.2f}s)")
        else:
            print(f"{provider.upper()}: ❌ ERROR - {result['error']}")
    
    # Check if any provider detected speech
    detected_speech = any(
        'error' not in results[p] and 
        bool(results[p].get('original_text', '').strip() or results[p].get('english_transcript', '').strip())
        for p in providers
    )
    
    if detected_speech:
        print("\n✅ At least one STT provider detected speech in synthetic audio!")
    else:
        print("\n⚠️  No STT provider detected speech. This suggests:")
        print("   1. Synthetic audio may not be realistic enough")
        print("   2. STT providers may require actual human speech")
        print("   3. Audio format or quality issues")
        print("\n💡 Recommendation: Test with real recorded human speech")

if __name__ == "__main__":
    main()
