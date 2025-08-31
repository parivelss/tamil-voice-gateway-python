"""
OpenAI LLM Adapter for Conversational AI
Handles Tamil/English mixed conversations with cultural context
"""

import openai
import logging
from typing import List, Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAILLMAdapter:
    """OpenAI LLM adapter for conversational AI"""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"
        self.conversation_history = []
        
    async def chat(self, user_message: str, language: str = "auto", should_summarize: bool = False) -> str:
        """
        Generate conversational response
        
        Args:
            user_message: User's message in Tamil or English
            language: Detected language of user message
            should_summarize: Whether to provide summary (compatibility parameter)
            
        Returns:
            AI response in appropriate language
        """
        try:
            # Debug: Check if API key is loaded
            if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "":
                logger.error("OpenAI API key is empty or not loaded")
                raise Exception("OpenAI API key not configured")
            
            logger.info(f"OpenAI API key loaded: {settings.OPENAI_API_KEY[:10]}...")
            
            # Add user message to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Keep conversation history manageable (last 10 exchanges)
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            # Create system prompt for Tamil/English conversation
            system_prompt = self._get_system_prompt(language)
            
            messages = [
                {"role": "system", "content": system_prompt},
                *self.conversation_history
            ]
            
            logger.info("Generating LLM response", extra={
                "message_length": len(user_message),
                "language": language,
                "history_length": len(self.conversation_history)
            })
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Add AI response to conversation history
            self.conversation_history.append({
                "role": "assistant", 
                "content": ai_response
            })
            
            logger.info("LLM response generated", extra={
                "response_length": len(ai_response),
                "tokens_used": response.usage.total_tokens
            })
            
            return ai_response
            
        except Exception as error:
            logger.error(f"LLM chat failed: {str(error)}", extra={
                "error_type": type(error).__name__,
                "error_details": str(error),
                "user_message": user_message[:100],
                "api_key_present": bool(settings.OPENAI_API_KEY)
            })
            
            # Check if it's a quota/billing issue
            if "quota" in str(error).lower() or "billing" in str(error).lower():
                logger.error("OpenAI API quota exceeded - need to add credits to account")
                if language == "ta":
                    return "மன்னிக்கவும், OpenAI API quota முடிந்துவிட்டது. API கீயில் credits சேர்க்க வேண்டும்."
                else:
                    return "Sorry, OpenAI API quota exceeded. Please add credits to your API account."
            
            # Check for authentication issues
            if "authentication" in str(error).lower() or "api_key" in str(error).lower():
                logger.error("OpenAI API authentication failed - check API key")
                if language == "ta":
                    return "மன்னிக்கவும், OpenAI API key சரியாக இல்லை. API key ஐ சரிபார்க்கவும்."
                else:
                    return "Sorry, OpenAI API authentication failed. Please check your API key."
            
            # Generic fallback for other errors
            if language == "ta":
                return "மன்னிக்கவும், தற்போது AI சேவையில் சிக்கல் உள்ளது. மீண்டும் முயற்சி செய்யுங்கள்."
            else:
                return "Sorry, there's currently an issue with the AI service. Please try again."
    
    def _get_system_prompt(self, language: str) -> str:
        """Get system prompt for conversational AI"""
        return """You are "Vaanga Pesalam" - a friendly Tamil conversational AI assistant.

PERSONALITY:
- Warm, friendly, and culturally aware
- Understands both Tamil and English
- Responds naturally in the same language as the user
- Uses colloquial, conversational Tamil (not formal literary Tamil)
- Knowledgeable about Tamil culture, traditions, and daily life

CONVERSATION STYLE:
- Keep responses conversational and natural
- Use appropriate Tamil greetings and expressions
- Mix languages naturally when appropriate (code-switching)
- Be helpful, engaging, and culturally sensitive
- Ask follow-up questions to keep conversation flowing

LANGUAGE GUIDELINES:
- If user speaks Tamil, respond in colloquial Tamil
- If user speaks English, respond in English
- If user mixes languages, feel free to mix as well
- Use everyday Tamil words, not complex literary terms

TOPICS YOU CAN DISCUSS:
- Daily life, family, work, studies
- Tamil culture, festivals, food, movies
- General knowledge and helpful advice
- Weather, travel, technology
- Personal interests and hobbies

Keep responses concise (2-3 sentences) and engaging. Always maintain a friendly, helpful tone."""

    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        logger.info("Conversation history reset")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get conversation statistics"""
        return {
            "message_count": len(self.conversation_history),
            "user_messages": len([msg for msg in self.conversation_history if msg["role"] == "user"]),
            "ai_messages": len([msg for msg in self.conversation_history if msg["role"] == "assistant"])
        }
