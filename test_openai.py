#!/usr/bin/env python3
"""
Test OpenAI API integration directly
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.adapters.openai_llm import OpenAILLMAdapter
from app.core.config import settings

async def test_openai_api():
    """Test OpenAI API with new key"""
    print("🤖 Testing OpenAI API Integration")
    print("=" * 50)
    
    # Check if API key is loaded
    print(f"OpenAI API Key loaded: {'✅' if settings.OPENAI_API_KEY else '❌'}")
    if settings.OPENAI_API_KEY:
        print(f"API Key starts with: {settings.OPENAI_API_KEY[:10]}...")
    
    # Test OpenAI adapter
    try:
        adapter = OpenAILLMAdapter()
        print("\n🔄 Testing OpenAI chat completion...")
        
        response = await adapter.chat("Hello, how are you?", language="en")
        print(f"✅ OpenAI Response: {response}")
        
        # Test Tamil response
        print("\n🔄 Testing Tamil conversation...")
        tamil_response = await adapter.chat("வணக்கம், எப்படி இருக்கீங்க?", language="ta")
        print(f"✅ Tamil Response: {tamil_response}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API Error: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_openai_api())
    if result:
        print("\n🎉 OpenAI integration working!")
    else:
        print("\n💥 OpenAI integration failed!")
