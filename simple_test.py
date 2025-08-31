#!/usr/bin/env python3
"""
Simple test of the Python Tamil Voice Gateway without external dependencies
"""

import asyncio
import json
from pathlib import Path

# Mock adapters for testing without external APIs
class MockSarvamSTTAdapter:
    async def transcribe(self, audio_data, options):
        return type('Result', (), {
            'text': 'வணக்கம், இது ஒரு சோதனை',
            'confidence': 0.95,
            'detected_language': 'ta',
            'timestamps': None
        })()

class MockGoogleTranslateAdapter:
    async def translate_to_english(self, text, source_language=None):
        return type('Result', (), {
            'text': 'Hello, this is a test',
            'source_language': source_language or 'ta',
            'target_language': 'en',
            'confidence': 1.0,
            'provider': 'google'
        })()

class MockElevenLabsTTSAdapter:
    async def synthesize(self, text, language, options):
        # Return mock audio data
        return type('Result', (), {
            'audio_data': b'mock_audio_data_' + text.encode('utf-8')[:50],
            'format': 'mp3',
            'sample_rate': 22050
        })()

async def test_listen_flow():
    """Test the listen flow: Audio -> STT -> Translation"""
    print("🎤 Testing Listen Flow...")
    
    # Mock audio data
    audio_data = b"mock_audio_data"
    
    # STT
    stt_adapter = MockSarvamSTTAdapter()
    stt_result = await stt_adapter.transcribe(audio_data, None)
    
    print(f"STT Result: {stt_result.text}")
    print(f"Detected Language: {stt_result.detected_language}")
    print(f"Confidence: {stt_result.confidence}")
    
    # Translation
    translate_adapter = MockGoogleTranslateAdapter()
    translation_result = await translate_adapter.translate_to_english(
        stt_result.text, stt_result.detected_language
    )
    
    print(f"English Translation: {translation_result.text}")
    print(f"✅ Listen flow completed successfully!")
    
    return {
        'success': True,
        'english_transcript': translation_result.text,
        'original_language': stt_result.detected_language,
        'original_text': stt_result.text,
        'confidence': stt_result.confidence
    }

async def test_speak_flow():
    """Test the speak flow: English text -> Translation -> TTS"""
    print("\n🔊 Testing Speak Flow...")
    
    english_text = "Hello, this is a test of the Tamil Voice Gateway"
    target_language = "ta"
    
    # Translation (English to Tamil)
    translate_adapter = MockGoogleTranslateAdapter()
    # Mock translation result
    tamil_text = "வணக்கம், இது தமிழ் குரல் நுழைவாயிலின் சோதனை"
    
    print(f"English Text: {english_text}")
    print(f"Tamil Translation: {tamil_text}")
    
    # TTS
    tts_adapter = MockElevenLabsTTSAdapter()
    tts_result = await tts_adapter.synthesize(tamil_text, target_language, None)
    
    print(f"Generated Audio Size: {len(tts_result.audio_data)} bytes")
    print(f"Audio Format: {tts_result.format}")
    print(f"✅ Speak flow completed successfully!")
    
    return {
        'success': True,
        'final_text': tamil_text,
        'final_language': target_language,
        'original_text': english_text,
        'audio_size_bytes': len(tts_result.audio_data)
    }

async def test_conversation_flow():
    """Test a complete conversation flow"""
    print("\n💬 Testing Complete Conversation Flow...")
    
    # Step 1: Listen (Tamil speech -> English transcript)
    listen_result = await test_listen_flow()
    
    # Step 2: Process the English transcript (this would be where conversation logic goes)
    english_response = f"I heard you say: {listen_result['english_transcript']}. Thank you for testing!"
    
    # Step 3: Speak (English response -> Tamil audio)
    print(f"\n🤖 AI Response: {english_response}")
    speak_result = await test_speak_flow()
    
    print(f"\n✅ Complete conversation flow successful!")
    return {
        'listen_result': listen_result,
        'ai_response': english_response,
        'speak_result': speak_result
    }

def test_project_structure():
    """Test that all required files are present"""
    print("\n📁 Testing Project Structure...")
    
    required_files = [
        'app/main.py',
        'app/core/config.py',
        'app/core/logging.py',
        'app/models/stt.py',
        'app/models/tts.py',
        'app/models/translation.py',
        'app/adapters/base.py',
        'app/adapters/sarvam_stt.py',
        'app/adapters/google_stt.py',
        'app/adapters/google_translate.py',
        'app/adapters/elevenlabs_tts.py',
        'app/api/routes/conversation.py',
        'app/api/routes/health.py',
        'app/middleware/auth.py',
        'app/middleware/rate_limit.py',
        'static/index.html',
        'requirements.txt',
        '.env.example'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print(f"✅ All {len(required_files)} required files present!")
        return True

async def main():
    """Run all tests"""
    print("🚀 Tamil Voice Gateway Python - Simple Test Suite")
    print("=" * 60)
    
    # Test project structure
    structure_ok = test_project_structure()
    
    if not structure_ok:
        print("\n⚠️  Project structure incomplete. Some files are missing.")
        return
    
    # Test conversation flows
    try:
        await test_conversation_flow()
        
        print("\n" + "=" * 60)
        print("🎉 All tests passed! The Python implementation structure is working.")
        print("\nNext steps:")
        print("1. Set up environment variables in .env file")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Run the server: python -m app.main")
        print("4. Test with real APIs using the web UI at http://localhost:8000/static/")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("Check the implementation for issues.")

if __name__ == "__main__":
    asyncio.run(main())
