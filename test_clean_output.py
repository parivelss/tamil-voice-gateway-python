#!/usr/bin/env python3
"""
Test script to verify clean Tamil output without instruction leakage
"""

import asyncio
import httpx
import json

async def test_clean_speak_output():
    """Test Speak module for clean Tamil output"""
    print("🧪 Testing Speak Module - Clean Output")
    print("=" * 50)
    
    test_cases = [
        "Take your medicine twice daily",
        "Your blood pressure is normal", 
        "Come for check-up next week",
        "What symptoms do you have?"
    ]
    
    url = "http://localhost:8005/v1/speak/preview"
    headers = {"Content-Type": "application/json", "x-skip-auth": "true"}
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {text}")
        
        payload = {
            "english_text": text,
            "target_language": "ta", 
            "voice_speed": 1.0,
            "voice_provider": "elevenlabs"
        }
        
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                
            if response.status_code == 200:
                result = response.json()
                tamil_text = result.get('final_text', '')
                
                print(f"✅ Tamil: {tamil_text}")
                
                # Check for instruction leakage
                instruction_indicators = [
                    'translate', 'output', 'respond', 'guidelines', 'style', 
                    'examples', 'avoid', 'use tamil', 'use english', 'doctor would say'
                ]
                
                has_instructions = any(indicator in tamil_text.lower() for indicator in instruction_indicators)
                
                if has_instructions:
                    print("❌ INSTRUCTION LEAK DETECTED!")
                else:
                    print("✅ Clean output - no instruction leakage")
                    
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

async def test_clean_vaanga_pesalam():
    """Test Vaanga Pesalam for clean responses"""
    print("\n\n🧪 Testing Vaanga Pesalam - Clean Responses")
    print("=" * 50)
    
    # Direct test with Gemini LLM adapter
    try:
        from app.adapters.gemini_llm import GeminiLLMAdapter
        
        gemini = GeminiLLMAdapter()
        test_messages = [
            "I have fever since morning",
            "My head is paining a lot", 
            "Blood pressure seems high",
            "Feeling very tired lately"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n👤 Patient: {message}")
            
            response = await gemini.chat(message, "en")
            print(f"🩺 Doctor: {response}")
            
            # Check for instruction leakage
            instruction_indicators = [
                'respond', 'use tamil', 'use english', 'examples', 'guidelines',
                'style', 'avoid', 'personality', 'role', 'conversation', 'language mixing',
                'translate', 'output only', 'dr. tamil', 'assistant'
            ]
            
            has_instructions = any(indicator in response.lower() for indicator in instruction_indicators)
            
            if has_instructions:
                print("❌ INSTRUCTION LEAK DETECTED!")
                print(f"🔍 Problematic content found in response")
            else:
                print("✅ Clean response - no instruction leakage")
                
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

async def main():
    """Run clean output tests"""
    print("🧹 Testing Clean Tamil Output (No Instruction Leakage)")
    print("🎯 Goal: Ensure ElevenLabs gets clean Tamil text")
    print("=" * 60)
    
    await test_clean_speak_output()
    await test_clean_vaanga_pesalam()
    
    print("\n" + "=" * 60)
    print("📊 CLEAN OUTPUT TEST SUMMARY")
    print("=" * 60)
    print("🎯 Objective: Remove all instruction text from Tamil output")
    print("🔊 ElevenLabs should receive only clean Tamil/English mixed text")
    print("🩺 Doctor responses should be natural without meta-instructions")

if __name__ == "__main__":
    asyncio.run(main())
