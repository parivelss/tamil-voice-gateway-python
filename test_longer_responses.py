#!/usr/bin/env python3
"""
Test script to verify Gemini generates longer, more detailed responses
"""

import asyncio

async def test_longer_gemini_responses():
    """Test Gemini for longer, more detailed responses"""
    print("🧪 Testing Gemini - Longer Response Generation")
    print("=" * 60)
    
    try:
        from app.adapters.gemini_llm import GeminiLLMAdapter
        
        gemini = GeminiLLMAdapter()
        
        # Test cases that should generate longer responses
        test_cases = [
            "I've been having headaches for 3 weeks, feeling dizzy, and having trouble sleeping. What could be wrong?",
            "My mother is 65 years old and has diabetes. She's been feeling weak lately and her sugar levels are fluctuating. What should we do?",
            "I'm planning to start exercising after being sedentary for years. I'm 45 years old with mild hypertension. What precautions should I take?",
            "My child has been coughing for a week, has mild fever on and off, and is not eating well. When should I be worried?"
        ]
        
        for i, message in enumerate(test_cases, 1):
            print(f"\n👤 Patient {i}: {message}")
            print(f"📏 Question length: {len(message)} characters")
            
            response = await gemini.chat(message, "en")
            
            print(f"🩺 Doctor: {response}")
            print(f"📏 Response length: {len(response)} characters")
            
            # Analyze response quality
            word_count = len(response.split())
            sentence_count = len([s for s in response.split('.') if s.strip()])
            
            if len(response) > 100:
                quality = "✅ Detailed response"
            elif len(response) > 50:
                quality = "⚠️ Medium response"
            else:
                quality = "❌ Too short"
                
            print(f"📊 Analysis: {word_count} words, ~{sentence_count} sentences - {quality}")
            
            # Check for instruction leakage
            has_instructions = any(word in response.lower() for word in 
                ['respond', 'guidelines', 'examples', 'style', 'avoid'])
            
            if has_instructions:
                print("❌ Instruction leakage detected")
            else:
                print("✅ Clean output")
                
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

async def main():
    """Run longer response tests"""
    print("🎯 Testing Gemini Response Length After Removing Restrictions")
    print("📏 Goal: Generate detailed, helpful doctor responses")
    print("=" * 60)
    
    await test_longer_gemini_responses()
    
    print("\n" + "=" * 60)
    print("📊 LONGER RESPONSE TEST SUMMARY")
    print("=" * 60)
    print("🎯 Removed: 'Keep responses short (1-2 sentences)' restriction")
    print("✅ Expected: More detailed, helpful medical advice")
    print("🩺 Style: Still colloquial Tamil doctor, but more comprehensive")

if __name__ == "__main__":
    asyncio.run(main())
