#!/usr/bin/env python3
"""
Test script to verify Gemini is now the true default everywhere
"""

import requests
import json
import base64

def create_test_audio():
    """Create minimal test audio data"""
    # Minimal WAV header + silence
    wav_data = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    return base64.b64encode(wav_data).decode()

def test_default_routing():
    """Test that Gemini is used by default without specifying llm_provider"""
    print("🔧 Testing Default Routing Fix")
    print("=" * 50)
    
    url = "http://localhost:8005/v1/vaanga-pesalam"
    headers = {
        "Content-Type": "application/json",
        "x-skip-auth": "true"
    }
    
    # Test 1: No llm_provider specified (should default to Gemini)
    payload1 = {
        "audio_data": create_test_audio(),
        "session_id": "test_default_routing",
        "stt_provider": "google"
        # NO llm_provider specified - should use Gemini default
    }
    
    print("\n1. Testing with NO llm_provider specified:")
    print(f"   Payload: {json.dumps({k:v for k,v in payload1.items() if k != 'audio_data'}, indent=2)}")
    
    try:
        response1 = requests.post(url, headers=headers, json=payload1, timeout=30)
        print(f"   Status: {response1.status_code}")
        
        if response1.status_code == 200:
            data = response1.json()
            ai_response = data.get('ai_response_text', '')
            
            # Check if it's Gemini response (should have வணக்கம் or caring doctor style)
            if 'வணக்கம்' in ai_response or 'கவலைப்படாதீங்க' in ai_response:
                print("   ✅ GEMINI DETECTED - Default routing working!")
                print(f"   Response: {ai_response[:100]}...")
            elif 'மன்னிக்கவும்' in ai_response and 'AI சேவையில்' in ai_response:
                print("   ❌ OPENAI DETECTED - Still using OpenAI as default")
                print(f"   Response: {ai_response[:100]}...")
            else:
                print("   ❓ UNKNOWN RESPONSE TYPE")
                print(f"   Response: {ai_response[:100]}...")
        else:
            print(f"   ❌ Request failed: {response1.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    # Test 2: Explicitly specify Gemini
    payload2 = {
        "audio_data": create_test_audio(),
        "session_id": "test_explicit_gemini",
        "stt_provider": "google",
        "llm_provider": "gemini"
    }
    
    print("\n2. Testing with explicit llm_provider='gemini':")
    try:
        response2 = requests.post(url, headers=headers, json=payload2, timeout=30)
        print(f"   Status: {response2.status_code}")
        
        if response2.status_code == 200:
            data = response2.json()
            ai_response = data.get('ai_response_text', '')
            
            if 'வணக்கம்' in ai_response or 'கவலைப்படாதீங்க' in ai_response:
                print("   ✅ GEMINI WORKING - Explicit selection works")
            else:
                print("   ❌ GEMINI NOT WORKING - Even explicit selection fails")
                
        else:
            print(f"   ❌ Request failed: {response2.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_default_routing()
