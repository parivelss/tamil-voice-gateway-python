#!/usr/bin/env python3
"""
Test script for improved conversation flow - no repetitive questions, progressive investigation
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.adapters.gemini_llm import GeminiLLMAdapter

async def test_progressive_investigation():
    """Test progressive questioning without repetition"""
    print("🔍 Testing Progressive Investigation Flow")
    print("=" * 60)
    
    # Initialize Gemini LLM adapter
    gemini_llm = GeminiLLMAdapter()
    
    # Simulate the exact conversation from the user's example
    conversation_flow = [
        {
            "patient": "எனக்கு கால் ரொம்ப வலிக்குது என்னதான் பண்றது",
            "expected": "Should greet and ask about onset/severity"
        },
        {
            "patient": "எனக்கும் முந்தாநேத்தில் இருந்து கால் வலி இன்டர்சிட்டி ஒரு 9/10 பயங்கரமா இருக்குது பொறுக்கவே முடியல",
            "expected": "Should NOT repeat onset/severity questions, ask about location/triggers"
        },
        {
            "patient": "Calf muscle-ல தான் வலி, walking பண்றப்போ அதிகமா வலிக்குது",
            "expected": "Should ask about associated symptoms or treatments tried"
        },
        {
            "patient": "Swelling கொஞ்சம் இருக்கு, medicine எதுவும் சாப்பிடல",
            "expected": "Should provide summary and doctor referral"
        }
    ]
    
    for i, exchange in enumerate(conversation_flow, 1):
        print(f"\n{i}. Patient: {exchange['patient']}")
        print(f"   Expected: {exchange['expected']}")
        
        try:
            # Check if this should trigger summary
            should_summarize = i >= 4  # After 4th exchange
            
            response = await gemini_llm.chat(
                user_message=exchange['patient'],
                language="ta",
                should_summarize=should_summarize
            )
            
            print(f"   Doctor: {response}")
            
            # Check for issues
            issues = []
            
            # Check for repetitive vanakkam
            if i > 1 and "வணக்கம்" in response:
                issues.append("❌ Repetitive vanakkam greeting")
            elif i == 1 and "வணக்கம்" not in response:
                issues.append("❌ Missing initial greeting")
            else:
                issues.append("✅ Appropriate greeting usage")
            
            # Check for repetitive questions
            if i == 2:  # Second response
                if "எப்போ" in response or "start" in response:
                    issues.append("❌ Repeating onset question")
                elif "எவ்வளவு" in response and "severe" in response:
                    issues.append("❌ Repeating severity question")
                else:
                    issues.append("✅ No repetitive questions")
            
            # Check for progressive questioning
            question_count = response.count('?')
            if question_count <= 2:
                issues.append(f"✅ Question limit respected: {question_count}")
            else:
                issues.append(f"❌ Too many questions: {question_count}")
            
            # Check for summary trigger
            if should_summarize and "senior doctor" in response:
                issues.append("✅ Summary and referral triggered")
            elif should_summarize:
                issues.append("❌ Summary not triggered when expected")
            
            for issue in issues:
                print(f"   {issue}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

async def test_memory_retention():
    """Test that AI remembers what patient has already told"""
    print(f"\n🧠 Testing Memory Retention")
    print("=" * 40)
    
    gemini_llm = GeminiLLMAdapter()
    
    # First exchange - establish baseline info
    response1 = await gemini_llm.chat("I have headache for 3 days, very severe", "en")
    print(f"1. Patient: I have headache for 3 days, very severe")
    print(f"   Doctor: {response1}")
    
    # Second exchange - should NOT ask about duration or severity again
    response2 = await gemini_llm.chat("It's getting worse", "en")
    print(f"\n2. Patient: It's getting worse")
    print(f"   Doctor: {response2}")
    
    # Check if doctor remembered previous info
    memory_check = []
    if "எப்போ" not in response2 and "start" not in response2:
        memory_check.append("✅ Didn't repeat onset question")
    else:
        memory_check.append("❌ Repeated onset question")
        
    if "எவ்வளவு" not in response2 and "severe" not in response2:
        memory_check.append("✅ Didn't repeat severity question")
    else:
        memory_check.append("❌ Repeated severity question")
    
    for check in memory_check:
        print(f"   {check}")

if __name__ == "__main__":
    asyncio.run(test_progressive_investigation())
    asyncio.run(test_memory_retention())
