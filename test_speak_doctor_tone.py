#!/usr/bin/env python3
"""
Test script for Speak module with comforting junior doctor translation tone
Tests various content types: questions, long explanations, medical advice
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.adapters.gemini_translate import GeminiTranslateAdapter

async def test_doctor_tone_translation():
    """Test Gemini translation with caring junior doctor tone"""
    print("🩺 Testing Speak Module - Caring Junior Doctor Translation")
    print("=" * 70)
    
    # Initialize Gemini translator
    translator = GeminiTranslateAdapter()
    
    # Test various content types
    test_cases = [
        {
            "english": "How are you feeling today?",
            "type": "Simple question",
            "expected_tone": "Caring and gentle"
        },
        {
            "english": "What symptoms are you experiencing? When did they start?",
            "type": "Medical questions",
            "expected_tone": "Professional but warm"
        },
        {
            "english": "Take this medicine twice a day after meals. Make sure to rest well and drink plenty of water. If your fever doesn't reduce, please come back tomorrow.",
            "type": "Long medical advice",
            "expected_tone": "Detailed, caring, reassuring"
        },
        {
            "english": "Don't worry, everything will be fine. We are here to help you.",
            "type": "Comforting message",
            "expected_tone": "Very reassuring and supportive"
        },
        {
            "english": "Your blood pressure is slightly high. We need to monitor it regularly. Please avoid salty foods and exercise daily.",
            "type": "Medical explanation",
            "expected_tone": "Informative but caring"
        },
        {
            "english": "I understand you're worried about your diabetes. Let me explain how to manage it properly with diet and medication.",
            "type": "Empathetic explanation",
            "expected_tone": "Understanding and educational"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['type']}")
        print(f"   English: \"{test_case['english']}\"")
        print(f"   Expected tone: {test_case['expected_tone']}")
        
        try:
            tamil_translation = await translator.translate_to_colloquial_tamil(test_case['english'])
            print(f"   Tamil: \"{tamil_translation}\"")
            
            # Check for caring elements
            caring_indicators = [
                "கவலைப்படாதீங்க",  # Don't worry
                "நாங்க இருக்கோம்",    # We are here
                "எல்லாம் சரியாகும்",   # Everything will be fine
                "நல்லா",              # Well/good
                "சரி",                # Okay/good
                "வணக்கம்"             # Greetings
            ]
            
            # Check for natural Tanglish mixing
            has_english_medical = any(word in tamil_translation for word in [
                "medicine", "fever", "blood pressure", "diabetes", "symptoms"
            ])
            
            # Check for Tamil script
            has_tamil_script = any('\u0b80' <= char <= '\u0bff' for char in tamil_translation)
            
            print(f"   ✅ Contains caring language: {any(indicator in tamil_translation for indicator in caring_indicators)}")
            print(f"   ✅ Natural Tanglish mixing: {has_english_medical and has_tamil_script}")
            print(f"   ✅ No instruction leakage: {'translate' not in tamil_translation.lower()}")
            
        except Exception as e:
            print(f"   ❌ Translation failed: {str(e)}")

async def test_question_vs_explanation_tone():
    """Test different tones for questions vs explanations"""
    print(f"\n🎭 Testing Tone Variation: Questions vs Explanations")
    print("=" * 60)
    
    translator = GeminiTranslateAdapter()
    
    comparison_tests = [
        {
            "question": "Are you taking your medicine regularly?",
            "explanation": "You should take your medicine regularly every day at the same time to maintain consistent levels in your blood."
        },
        {
            "question": "How is your pain level today?",
            "explanation": "Pain management is important for your recovery. We can adjust your medication if the current dose isn't providing adequate relief."
        }
    ]
    
    for i, test in enumerate(comparison_tests, 1):
        print(f"\n{i}. Comparison Test")
        
        # Translate question
        question_tamil = await translator.translate_to_colloquial_tamil(test['question'])
        print(f"   Question: \"{test['question']}\"")
        print(f"   Tamil: \"{question_tamil}\"")
        
        # Translate explanation
        explanation_tamil = await translator.translate_to_colloquial_tamil(test['explanation'])
        print(f"   Explanation: \"{test['explanation']}\"")
        print(f"   Tamil: \"{explanation_tamil}\"")
        
        # Analyze tone differences
        question_has_question_mark = '?' in question_tamil
        explanation_length = len(explanation_tamil.split())
        
        print(f"   ✅ Question format preserved: {question_has_question_mark}")
        print(f"   ✅ Explanation is detailed: {explanation_length > 10}")

if __name__ == "__main__":
    asyncio.run(test_doctor_tone_translation())
    asyncio.run(test_question_vs_explanation_tone())
