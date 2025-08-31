#!/usr/bin/env python3
"""
Test all API integrations and quotas
"""

import asyncio
import sys
import os
import base64
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.adapters.sarvam_stt import SarvamSTTAdapter
from app.adapters.google_stt import GoogleSTTAdapter
from app.adapters.elevenlabs_tts import ElevenLabsTTSAdapter
from app.adapters.google_translate import GoogleTranslateAdapter
from app.adapters.openai_llm import OpenAILLMAdapter
from app.models.stt import STTOptions, STTProvider
from app.models.tts import TTSOptions, TTSProvider
from app.core.config import settings

async def test_all_apis():
    """Test all API integrations and check quotas"""
    print("🔍 Testing All API Integrations & Quotas")
    print("=" * 60)
    
    results = {}
    
    # 1. Test OpenAI API
    print("\n🤖 Testing OpenAI API...")
    try:
        openai_adapter = OpenAILLMAdapter()
        response = await openai_adapter.chat("Test message", language="en")
        print(f"✅ OpenAI: Working - {response[:50]}...")
        results['openai'] = True
    except Exception as e:
        print(f"❌ OpenAI Error: {str(e)}")
        results['openai'] = False
    
    # 2. Test Sarvam STT API
    print("\n🎤 Testing Sarvam STT API...")
    try:
        sarvam_adapter = SarvamSTTAdapter()
        # Create a small test audio (silence)
        test_audio = b'\x00' * 1024  # 1KB of silence
        stt_options = STTOptions(language="auto", provider=STTProvider.SARVAM)
        response = await sarvam_adapter.transcribe(test_audio, stt_options)
        print(f"✅ Sarvam STT: Working - Response: {response}")
        results['sarvam'] = True
    except Exception as e:
        print(f"❌ Sarvam STT Error: {str(e)}")
        results['sarvam'] = False
    
    # 3. Test Google Cloud STT API
    print("\n🎤 Testing Google Cloud STT API...")
    try:
        google_stt_adapter = GoogleSTTAdapter()
        test_audio = b'\x00' * 1024  # 1KB of silence
        stt_options = STTOptions(language="auto", provider=STTProvider.GOOGLE)
        response = await google_stt_adapter.transcribe(test_audio, stt_options)
        print(f"✅ Google STT: Working - Response: {response}")
        results['google_stt'] = True
    except Exception as e:
        print(f"❌ Google STT Error: {str(e)}")
        results['google_stt'] = False
    
    # 4. Test ElevenLabs TTS API
    print("\n🔊 Testing ElevenLabs TTS API...")
    try:
        elevenlabs_adapter = ElevenLabsTTSAdapter()
        tts_options = TTSOptions(language="en", provider=TTSProvider.ELEVENLABS, voice_speed=1.0)
        audio_data = await elevenlabs_adapter.synthesize("Test message", tts_options)
        print(f"✅ ElevenLabs TTS: Working - Generated {len(audio_data)} bytes")
        results['elevenlabs'] = True
    except Exception as e:
        print(f"❌ ElevenLabs TTS Error: {str(e)}")
        results['elevenlabs'] = False
    
    # 5. Test Google Translate API
    print("\n🌐 Testing Google Translate API...")
    try:
        translate_adapter = GoogleTranslateAdapter()
        response = await translate_adapter.translate("Hello world", target_language="ta")
        print(f"✅ Google Translate: Working - {response}")
        results['google_translate'] = True
    except Exception as e:
        print(f"❌ Google Translate Error: {str(e)}")
        results['google_translate'] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 API STATUS SUMMARY:")
    working = sum(results.values())
    total = len(results)
    
    for api, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {api.upper()}: {'Working' if status else 'Failed'}")
    
    print(f"\n🎯 Overall: {working}/{total} APIs working")
    
    if working == total:
        print("🎉 All APIs are working! Ready for production.")
    else:
        print("⚠️  Some APIs have issues. Check the errors above.")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(test_all_apis())
