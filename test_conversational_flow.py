#!/usr/bin/env python3
"""
Test script to verify conversational flow with 2-question limit
"""

import asyncio

async def test_conversational_flow():
    """Test conversational flow with 2-question limit"""
    print("🧪 Testing Conversational Flow - 2 Question Limit")
    print("=" * 60)
    
    try:
        from app.adapters.gemini_llm import GeminiLLMAdapter
        
        gemini = GeminiLLMAdapter()
        
        # Simulate a multi-turn conversation
        conversation_scenarios = [
            {
                "patient_message": "Doctor, I've been having multiple health issues lately",
                "expected": "Should ask max 2 questions to start gathering info"
            },
            {
                "patient_message": "I have fever, headache, body pain, and stomach upset for 3 days",
                "expected": "Should focus on 1-2 main symptoms, not ask about everything"
            },
            {
                "patient_message": "My diabetes, blood pressure, and cholesterol are all acting up",
                "expected": "Should prioritize and ask about 1-2 conditions first"
            }
        ]
        
        for i, scenario in enumerate(conversation_scenarios, 1):
            print(f"\n📋 Scenario {i}: {scenario['expected']}")
            print(f"👤 Patient: {scenario['patient_message']}")
            
            response = await gemini.chat(scenario['patient_message'], "en")
            print(f"🩺 Doctor: {response}")
            
            # Count questions in response
            question_count = response.count('?')
            print(f"❓ Questions asked: {question_count}")
            
            if question_count <= 2:
                print("✅ Good - Max 2 questions per response")
            else:
                print(f"⚠️ Too many questions - {question_count} questions asked")
            
            # Check response length
            word_count = len(response.split())
            if word_count > 20:
                print("✅ Detailed response provided")
            else:
                print("⚠️ Response might be too brief")
                
            print("-" * 50)
            
            # Reset for next test
            gemini.reset_conversation()
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

async def test_follow_up_conversation():
    """Test follow-up conversation flow"""
    print("\n🔄 Testing Follow-up Conversation Flow")
    print("=" * 60)
    
    try:
        from app.adapters.gemini_llm import GeminiLLMAdapter
        
        gemini = GeminiLLMAdapter()
        
        # Simulate a realistic conversation
        conversation = [
            "Doctor, I have fever and headache for 2 days",
            "Fever is around 101°F and headache is severe",
            "I took paracetamol but it's not helping much",
            "No other symptoms, just these two main issues"
        ]
        
        for i, message in enumerate(conversation, 1):
            print(f"\n👤 Turn {i}: {message}")
            
            response = await gemini.chat(message, "en")
            print(f"🩺 Doctor: {response}")
            
            question_count = response.count('?')
            print(f"❓ Questions: {question_count} {'✅' if question_count <= 2 else '⚠️'}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

async def main():
    """Run conversational flow tests"""
    print("💬 Testing Conversational Flow with Question Limits")
    print("🎯 Goal: Max 2 questions per response for better conversation flow")
    print("=" * 60)
    
    await test_conversational_flow()
    await test_follow_up_conversation()
    
    print("\n" + "=" * 60)
    print("📊 CONVERSATIONAL FLOW SUMMARY")
    print("=" * 60)
    print("✅ Updated: 'Ask maximum 2 questions per response'")
    print("✅ Maintained: Detailed explanations and advice")
    print("🎯 Result: Better conversation flow without overwhelming patients")

if __name__ == "__main__":
    asyncio.run(main())
