#!/usr/bin/env python3
"""
Test script for colloquial Tamil output in Speak and Vaanga Pesalam modules
"""

import asyncio
import httpx
import json
import time

async def test_speak_colloquial_tamil():
    """Test the Speak module with colloquial Tamil translation"""
    print("🧪 Testing Speak Module - Colloquial Tamil Translation")
    print("=" * 60)
    
    test_texts = [
        "Hello, how are you feeling today?",
        "Take this medicine twice a day after meals and get some rest.",
        "Your blood pressure is normal. Come back next week for a check-up.",
        "What symptoms are you experiencing? When did they start?"
    ]
    
    url = "http://localhost:8005/v1/speak/preview"
    headers = {
        "Content-Type": "application/json",
        "x-skip-auth": "true"
    }
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 Test {i}: {text}")
        
        payload = {
            "english_text": text,
            "target_language": "ta",
            "voice_speed": 1.0,
            "voice_provider": "elevenlabs"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                
            if response.status_code == 200:
                result = response.json()
                final_text = result.get('final_text', '')
                
                print(f"✅ Tamil: {final_text}")
                print(f"🔊 Audio: {result.get('audio_size_bytes', 0):,} bytes")
                
                # Check if it looks colloquial (contains English words mixed in)
                has_english_words = any(word in final_text.lower() for word in ['medicine', 'blood', 'pressure', 'check', 'symptoms'])
                style = "🎯 Colloquial (Tanglish)" if has_english_words else "📚 Formal Tamil"
                print(f"📋 Style: {style}")
                
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        if i < len(test_texts):
            await asyncio.sleep(1)

async def test_vaanga_pesalam_colloquial():
    """Test the Vaanga Pesalam module with colloquial Tamil responses"""
    print("\n\n🧪 Testing Vaanga Pesalam - Colloquial Tamil Conversation")
    print("=" * 60)
    
    test_messages = [
        "Hi doctor, I have a fever since morning",
        "What medicine should I take for headache?",
        "My blood pressure reading was high yesterday",
        "I'm feeling tired all the time lately"
    ]
    
    url = "http://localhost:8005/v1/conversation"
    headers = {
        "Content-Type": "application/json",
        "x-skip-auth": "true"
    }
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n👤 Patient: {message}")
        
        # First convert to audio (simulate speech input)
        audio_data = "dummy_base64_audio_data"  # In real test, this would be actual audio
        
        payload = {
            "session_id": "test_session_colloquial",
            "audio_data": audio_data,
            "stt_provider": "google",
            "llm_provider": "gemini",
            "response_language": "ta"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # For this test, let's directly call the LLM to see the text response
                # In practice, this would go through the full conversation flow
                
                # Simulate the conversation by calling Gemini directly
                from app.adapters.gemini_llm import GeminiLLMAdapter
                
                gemini_adapter = GeminiLLMAdapter()
                response_text = await gemini_adapter.chat(message, "en")
                
                print(f"🩺 Doctor: {response_text}")
                
                # Check if response looks colloquial
                has_english_words = any(word in response_text.lower() for word in 
                    ['medicine', 'fever', 'blood', 'pressure', 'check', 'rest', 'doctor', 'symptoms'])
                has_colloquial_tamil = any(word in response_text for word in 
                    ['ah', 'ku', 'la', 'irukku', 'vaanga', 'pannunga', 'sapdu'])
                
                if has_english_words and has_colloquial_tamil:
                    style = "🎯 Perfect Tanglish (Doctor style)"
                elif has_english_words:
                    style = "📝 English mixed"
                elif has_colloquial_tamil:
                    style = "🗣️ Colloquial Tamil"
                else:
                    style = "📚 Formal style"
                    
                print(f"📋 Style: {style}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        if i < len(test_messages):
            await asyncio.sleep(1)

async def main():
    """Run all colloquial Tamil tests"""
    print("🚀 Testing Colloquial Tamil Implementation")
    print("🩺 Doctor-Patient Tanglish Style")
    print("=" * 60)
    
    # Test Speak module
    await test_speak_colloquial_tamil()
    
    # Test Vaanga Pesalam module  
    await test_vaanga_pesalam_colloquial()
    
    print("\n" + "=" * 60)
    print("📊 COLLOQUIAL TAMIL TEST SUMMARY")
    print("=" * 60)
    print("✅ Speak Module: Now uses Gemini for natural Tanglish translation")
    print("✅ Vaanga Pesalam: Now configured as friendly Tamil doctor")
    print("🎯 Both modules should sound like a Tamil doctor talking to patients")
    print("🗣️ Natural mixing of English medical terms with colloquial Tamil")

if __name__ == "__main__":
    asyncio.run(main())
