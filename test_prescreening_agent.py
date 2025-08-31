#!/usr/bin/env python3
"""
Test script for pre-screening junior doctor agent functionality
Tests the new workflow: information gathering -> comforting -> doctor referral
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.adapters.gemini_llm import GeminiLLMAdapter

async def test_prescreening_workflow():
    """Test the complete pre-screening agent workflow"""
    print("🩺 Testing Pre-screening Junior Doctor Agent")
    print("=" * 60)
    
    # Initialize Gemini LLM adapter
    gemini_llm = GeminiLLMAdapter()
    
    # Test conversation flow
    test_scenarios = [
        {
            "patient_input": "I have fever and headache",
            "description": "Initial symptoms presentation"
        },
        {
            "patient_input": "It started 2 days ago, temperature is around 101F",
            "description": "Providing symptom details"
        },
        {
            "patient_input": "I'm really worried, is it serious?",
            "description": "Patient expressing worry"
        },
        {
            "patient_input": "I also have some body aches and feel tired",
            "description": "Additional symptoms"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n👤 Patient ({scenario['description']}): {scenario['patient_input']}")
        
        # Check if this should trigger summary/closure
        should_summarize = i >= 3  # After 3rd exchange
        
        try:
            response = await gemini_llm.chat(
                user_message=scenario['patient_input'],
                language="en",
                should_summarize=should_summarize
            )
            
            print(f"🩺 Junior Doctor: {response}")
            
            # Check for comforting language
            comforting_phrases = ["கவலைப்படாதீங்க", "நாங்க இருக்கோம்", "எல்லாம் சரியாகும்"]
            has_comfort = any(phrase in response for phrase in comforting_phrases)
            
            # Check for question limiting
            question_count = response.count('?')
            
            print(f"   ✅ Comforting language: {'Yes' if has_comfort else 'No'}")
            print(f"   ✅ Questions asked: {question_count} (limit: 2)")
            
            # Check if closure message is triggered
            if should_summarize and "senior doctor" in response:
                print(f"   ✅ Doctor referral triggered: Yes")
                
                # Generate summary for doctor
                summary = await gemini_llm.generate_doctor_summary()
                print(f"\n📋 Doctor Summary Generated:")
                print(f"   {summary}")
                break
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print(f"\n📊 Conversation Statistics:")
    stats = gemini_llm.get_conversation_summary()
    print(f"   Total messages: {stats['message_count']}")
    print(f"   Patient messages: {stats['user_messages']}")
    print(f"   Doctor responses: {stats['ai_messages']}")

async def test_comfort_responses():
    """Test specific comforting responses for worried patients"""
    print(f"\n🤗 Testing Comfort Responses")
    print("=" * 40)
    
    gemini_llm = GeminiLLMAdapter()
    
    worried_inputs = [
        "I'm very scared about my symptoms",
        "Am I going to be okay?",
        "This pain is really worrying me"
    ]
    
    for worry in worried_inputs:
        print(f"\n👤 Worried Patient: {worry}")
        
        try:
            response = await gemini_llm.chat(
                user_message=worry,
                language="en"
            )
            
            print(f"🩺 Comforting Doctor: {response}")
            
            # Check for reassuring elements
            comfort_indicators = [
                "கவலைப்படாதீங்க",  # Don't worry
                "நாங்க இருக்கோம்",    # We are here
                "எல்லாம் சரியாகும்",   # Everything will be fine
                "help"
            ]
            
            comfort_score = sum(1 for indicator in comfort_indicators if indicator in response)
            print(f"   ✅ Comfort score: {comfort_score}/4")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_prescreening_workflow())
    asyncio.run(test_comfort_responses())
