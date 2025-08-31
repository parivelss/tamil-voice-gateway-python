#!/usr/bin/env python3
"""
Test script for Tamil Voice Gateway Python APIs
"""

import asyncio
import base64
import json
import time
from pathlib import Path
import httpx

# Configuration
BASE_URL = "http://localhost:8000"
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJ0ZXN0LXVzZXItMTIzIiwiZW1haWwiOiJ0ZXN0QHRhbWlsdm9pY2UuY29tIiwibmFtZSI6IlRlc3QgVXNlciIsImlhdCI6MTcwMDAwMDAwMCwiZXhwIjoyMDAwMDAwMDAwfQ.test-signature"

async def test_health_check():
    """Test health check endpoint"""
    print("🏥 Testing health check...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health/")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False

async def test_listen_api_with_sample():
    """Test /v1/listen API with sample text-to-speech audio"""
    print("\n🎤 Testing /v1/listen API...")
    
    # Create a simple test audio (silence for demo)
    # In real usage, you'd use actual audio file
    sample_audio = b'\x00' * 1000  # Simple silence
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            files = {"audio": ("test.wav", sample_audio, "audio/wav")}
            data = {
                "stt_provider": "sarvam",
                "timestamps": "false"
            }
            headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
            
            response = await client.post(
                f"{BASE_URL}/v1/listen",
                files=files,
                data=data,
                headers=headers
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {result.get('english_transcript', 'N/A')}")
                print(f"Provider: {result.get('stt_provider', 'N/A')}")
                print(f"Processing time: {result.get('processing_time_sec', 'N/A')}s")
                return True
            else:
                print(f"❌ Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Listen API test failed: {e}")
            return False

async def test_speak_api():
    """Test /v1/speak API"""
    print("\n🔊 Testing /v1/speak API...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            payload = {
                "english_text": "Hello, this is a test of the Tamil Voice Gateway.",
                "target_language": "ta",
                "voice_speed": 1.0,
                "voice_provider": "elevenlabs"
            }
            headers = {
                "Authorization": f"Bearer {TEST_TOKEN}",
                "Content-Type": "application/json"
            }
            
            response = await client.post(
                f"{BASE_URL}/v1/speak",
                json=payload,
                headers=headers
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                # Save audio to file
                audio_data = response.content
                output_file = Path("test_output.mp3")
                output_file.write_bytes(audio_data)
                
                processing_time = response.headers.get('X-Processing-Time', 'N/A')
                final_language = response.headers.get('X-Final-Language', 'N/A')
                
                print(f"✅ Success: Audio saved to {output_file}")
                print(f"Final language: {final_language}")
                print(f"Processing time: {processing_time}s")
                print(f"Audio size: {len(audio_data)} bytes")
                return True
            else:
                print(f"❌ Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Speak API test failed: {e}")
            return False

async def test_speak_preview_api():
    """Test /v1/speak/preview API"""
    print("\n🎵 Testing /v1/speak/preview API...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            payload = {
                "english_text": "This is a preview test.",
                "target_language": "en",
                "voice_speed": 1.2,
                "voice_provider": "elevenlabs"
            }
            headers = {
                "Authorization": f"Bearer {TEST_TOKEN}",
                "Content-Type": "application/json"
            }
            
            response = await client.post(
                f"{BASE_URL}/v1/speak/preview",
                json=payload,
                headers=headers
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {result.get('success', False)}")
                print(f"Final text: {result.get('final_text', 'N/A')}")
                print(f"Final language: {result.get('final_language', 'N/A')}")
                print(f"Audio size: {result.get('audio_size_bytes', 'N/A')} bytes")
                print(f"Processing time: {result.get('processing_time_sec', 'N/A')}s")
                
                # Optionally save base64 audio
                if result.get('audio_base64'):
                    audio_data = base64.b64decode(result['audio_base64'])
                    output_file = Path("test_preview.mp3")
                    output_file.write_bytes(audio_data)
                    print(f"Preview audio saved to {output_file}")
                
                return True
            else:
                print(f"❌ Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Speak preview API test failed: {e}")
            return False

async def main():
    """Run all API tests"""
    print("🚀 Starting Tamil Voice Gateway Python API Tests")
    print(f"Base URL: {BASE_URL}")
    print("=" * 60)
    
    results = []
    
    # Test health check
    results.append(await test_health_check())
    
    # Test conversation APIs
    results.append(await test_listen_api_with_sample())
    results.append(await test_speak_api())
    results.append(await test_speak_preview_api())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"✅ Passed: {sum(results)}/{len(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! Tamil Voice Gateway Python is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
        print("\nTroubleshooting:")
        print("1. Make sure the Python server is running: python -m app.main")
        print("2. Check if all environment variables are set in .env")
        print("3. Verify API keys for Sarvam, Google Cloud, and ElevenLabs")
        print("4. Check server logs for detailed error information")

if __name__ == "__main__":
    asyncio.run(main())
