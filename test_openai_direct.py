#!/usr/bin/env python3
"""
Test OpenAI API directly to verify if the key is working
"""

import asyncio
import openai
from app.core.config import settings

async def test_openai_direct():
    """Test OpenAI API directly"""
    print("Testing OpenAI API directly...")
    print(f"API Key: {settings.OPENAI_API_KEY[:20]}...")
    
    try:
        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Say hello in Tamil"}
            ],
            max_tokens=50
        )
        
        print(f"✅ SUCCESS: {response.choices[0].message.content}")
        print(f"Tokens used: {response.usage.total_tokens}")
        return True
        
    except Exception as error:
        print(f"❌ FAILED: {error}")
        print(f"Error type: {type(error).__name__}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_openai_direct())
    if result:
        print("\n✅ OpenAI API key is working correctly!")
    else:
        print("\n❌ OpenAI API key has issues.")
