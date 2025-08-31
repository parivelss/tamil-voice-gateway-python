#!/usr/bin/env python3
"""
Test final conversational flow with 2-question limit and detailed answers
"""

import asyncio

async def test_final_conversational_flow():
    """Test the final conversational flow"""
    print("🧪 Testing Final Conversational Flow")
    print("=" * 50)
    
    try:
        from app.adapters.gemini_llm import GeminiLLMAdapter
        
        gemini = GeminiLLMAdapter()
        
        test_cases = [
            "I have multiple symptoms - fever, headache, and stomach pain",
            "My diabetes and blood pressure are both high today",
            "Tell me about diabetes management and diet control"
        ]
        
        for i, message in enumerate(test_cases, 1):
            print(f"\n👤 Patient: {message}")
            
            response = await gemini.chat(message, "en")
            print(f"🩺 Doctor: {response}")
            
            # Count questions
            question_count = response.count('?')
            print(f"❓ Questions: {question_count} {'✅' if question_count <= 2 else '❌'}")
            
            # Check response quality
            word_count = len(response.split())
            print(f"📏 Length: {len(response)} chars, {word_count} words")
            
            gemini.reset_conversation()
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_final_conversational_flow())
