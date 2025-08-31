#!/usr/bin/env python3
"""
Test script to verify fixed conversation flow - no repetitive greetings or questions
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.adapters.gemini_llm import GeminiLLMAdapter

async def test_fixed_conversation():
    """Test the fixed conversation flow"""
    print("🔧 Testing Fixed Conversation Flow")
    print("=" * 50)
    
    # Initialize Gemini LLM adapter
    gemini_llm = GeminiLLMAdapter()
    
    # Test the exact problematic scenario
    conversation = [
        "டாக்டர் எனக்கு காலைல இருந்து ரொம்ப தலை வலிக்குது என்ன பண்றதுன்னே தெரிய மாட்டேங்குது",
        "காலைல இருந்து start ஆச்சு, pain level 8/10 இருக்கு",
        "Forehead-ல தான் pain இருக்கு, bright light பார்த்தா அதிகமா வலிக்குது",
        "வேற symptoms எதுவும் இல்ல, medicine எதுவும் சாப்பிடல"
    ]
    
    for i, user_input in enumerate(conversation, 1):
        print(f"\n{i}. Patient: {user_input}")
        
        try:
            should_summarize = i >= 4  # After 4th exchange
            
            response = await gemini_llm.chat(
                user_message=user_input,
                language="ta",
                should_summarize=should_summarize
            )
            
            print(f"   Doctor: {response}")
            
            # Check for issues
            issues = []
            
            # Check vanakkam repetition
            if i > 1 and "வணக்கம்" in response:
                issues.append("❌ Repetitive vanakkam")
            elif i == 1 and "வணக்கம்" not in response:
                issues.append("❌ Missing initial greeting")
            else:
                issues.append("✅ Appropriate greeting")
            
            # Check for repetitive questions
            if i == 2:  # Second response should not repeat onset questions
                if "எப்போ" in response or "start" in response:
                    issues.append("❌ Repeating onset question")
                else:
                    issues.append("✅ No repetitive questions")
            
            # Check question count
            question_count = response.count('?')
            if question_count <= 2:
                issues.append(f"✅ Question limit: {question_count}")
            else:
                issues.append(f"❌ Too many questions: {question_count}")
            
            # Check for summary
            if should_summarize and "senior doctor" in response:
                issues.append("✅ Summary triggered")
            
            for issue in issues:
                print(f"   {issue}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_fixed_conversation())
