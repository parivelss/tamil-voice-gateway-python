#!/usr/bin/env python3
"""
Simple test for Speak module without audio recording dependencies
"""

import requests
import json

def test_speak_api():
    """Test Speak API directly"""
    print("Testing Speak API...")
    
    url = "http://localhost:8005/v1/speak"
    headers = {
        "Content-Type": "application/json",
        "x-skip-auth": "true"
    }
    
    payload = {
        "english_text": "Hello world, this is a test",
        "target_language": "en", 
        "voice_speed": 1.0,
        "voice_provider": "elevenlabs"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print(f"✅ SUCCESS: Audio generated ({len(response.content)} bytes)")
            
            # Save the audio file
            with open("test_speak_output.mp3", "wb") as f:
                f.write(response.content)
            print("Audio saved as test_speak_output.mp3")
            return True
        else:
            print(f"❌ FAILED: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def test_health_api():
    """Test health endpoint"""
    print("Testing Health API...")
    
    try:
        response = requests.get("http://localhost:8005/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Health check passed: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Health check exception: {e}")
        return False

if __name__ == "__main__":
    print("=== Tamil Voice Gateway Simple Test ===")
    
    # Test health first
    health_ok = test_health_api()
    print()
    
    # Test speak if health is ok
    if health_ok:
        speak_ok = test_speak_api()
        
        if speak_ok:
            print("\n✅ All tests passed! The Speak module is working.")
        else:
            print("\n❌ Speak module test failed.")
    else:
        print("\n❌ Server health check failed.")
