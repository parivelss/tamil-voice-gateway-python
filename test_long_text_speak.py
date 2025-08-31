#!/usr/bin/env python3
"""
Test script for Speak module with longer texts
"""

import asyncio
import httpx
import json
import time

# Test with progressively longer texts
test_texts = [
    # Short text (should work with old code)
    "Hello, how are you today?",
    
    # Medium text (around 500 chars)
    "This is a medium length text that should test the improved TTS system. It contains multiple sentences and should be processed without any issues. The system should handle this gracefully and produce high-quality audio output for the user to listen to.",
    
    # Long text (around 1000 chars)
    "This is a much longer text that will test the chunking functionality of the improved TTS system. It contains multiple sentences and paragraphs that need to be processed efficiently. The system should break this down into smaller chunks, process each chunk individually, and then combine the audio outputs seamlessly. This approach ensures that even very long texts can be converted to speech without hitting API limitations or causing system failures. The user should receive a complete audio file that sounds natural and continuous.",
    
    # Very long text (around 3000+ chars)
    """This is an extremely long text that will thoroughly test the advanced chunking capabilities of the Tamil Voice Gateway TTS system. The system has been designed to handle texts of various lengths by intelligently breaking them down into manageable chunks at sentence boundaries. This ensures that the natural flow and rhythm of speech are maintained even when processing very long content.

The chunking algorithm first attempts to split text at sentence endings, which preserves the natural pauses and intonation patterns that make speech sound more human-like. If sentences are still too long, the system falls back to word-level splitting to ensure that no chunk exceeds the API limits.

Each chunk is processed individually through the ElevenLabs TTS API, and the resulting audio segments are then concatenated to produce a seamless final output. This approach allows the system to handle everything from short phrases to long articles, books, or documentation while maintaining consistent voice quality and natural speech patterns.

The implementation includes proper error handling, logging, and monitoring to ensure reliability and debuggability. Users can now confidently use the Speak module with texts of any reasonable length without worrying about character limits or system failures."""
]

async def test_speak_endpoint(text: str, test_name: str):
    """Test the speak endpoint with given text"""
    print(f"\n🧪 Testing {test_name}")
    print(f"📝 Text length: {len(text)} characters")
    print(f"📄 Text preview: {text[:100]}...")
    
    url = "http://localhost:8005/v1/speak/preview"
    
    payload = {
        "english_text": text,
        "target_language": "ta",
        "voice_speed": 1.0,
        "voice_provider": "elevenlabs"
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-skip-auth": "true"
    }
    
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            audio_size = result.get('audio_size_bytes', 0)
            final_text = result.get('final_text', '')
            
            print(f"✅ SUCCESS")
            print(f"⏱️  Processing time: {processing_time:.2f} seconds")
            print(f"🔊 Audio size: {audio_size:,} bytes")
            print(f"🌐 Final text length: {len(final_text)} characters")
            print(f"📝 Final text preview: {final_text[:100]}...")
            
            return True
            
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"📄 Error: {response.text}")
            return False
            
    except Exception as e:
        processing_time = time.time() - start_time
        print(f"❌ EXCEPTION after {processing_time:.2f}s: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Speak Module Long Text Tests")
    print("=" * 60)
    
    results = []
    
    for i, text in enumerate(test_texts, 1):
        test_name = f"Test {i} ({len(text)} chars)"
        success = await test_speak_endpoint(text, test_name)
        results.append((test_name, success))
        
        # Wait between tests to avoid rate limiting
        if i < len(test_texts):
            print("⏳ Waiting 2 seconds...")
            await asyncio.sleep(2)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Speak module works with longer texts.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
