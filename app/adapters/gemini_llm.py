"""
Google Gemini LLM Adapter
"""

import logging
import google.generativeai as genai
from typing import List, Dict, Any, Optional

from app.core.config import settings
from app.models.llm import LLMResult, ConversationMessage
from app.adapters.base import LLMAdapter

logger = logging.getLogger(__name__)


class GeminiLLMAdapter(LLMAdapter):
    """Google Gemini LLM adapter"""
    
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.conversation_history = []
        
    async def chat(self, user_message: str, language: str = "auto", conversation_history: Optional[List[ConversationMessage]] = None, should_summarize: bool = False) -> str:
        """
        Generate chat response using Google Gemini
        
        Args:
            user_message: User's message
            language: Detected language
            conversation_history: Previous conversation messages
            
        Returns:
            AI response text
        """
        try:
            logger.info("Starting Gemini chat", extra={
                "message_length": len(user_message),
                "language": language,
                "history_length": len(conversation_history) if conversation_history else 0
            })
            
            # Create system prompt
            system_prompt = self._create_system_prompt(language)
            
            # Add user message to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Keep conversation history manageable (last 20 messages)
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            # Build conversation context
            conversation_text = system_prompt + "\n\n"
            
            if self.conversation_history:
                for msg in self.conversation_history[-10:]:  # Keep last 10 messages
                    role = "Human" if msg["role"] == "user" else "Assistant"
                    conversation_text += f"{role}: {msg['content']}\n"
            
            conversation_text += f"Human: {user_message}\nAssistant:"
            
            # Check if we should provide a summary and closure
            # Only summarize if we have gathered sufficient information through multiple exchanges
            if should_summarize and len(self.conversation_history) >= 6:  # At least 3 exchanges
                # Check if we have enough investigative details
                patient_responses = [msg["content"] for msg in self.conversation_history if msg["role"] == "user"]
                total_patient_info = " ".join(patient_responses).lower()
                
                # Look for key investigative elements
                has_duration = any(word in total_patient_info for word in ["day", "week", "month", "நாள", "வாரம்", "மாசம்", "yesterday", "நேத்து"])
                has_severity = any(word in total_patient_info for word in ["pain", "severe", "mild", "வலி", "அதிகம்", "கம்மி"]) or any(char.isdigit() for char in total_patient_info)
                has_location = any(word in total_patient_info for word in ["leg", "head", "chest", "கால்", "தலை", "மார்பு", "stomach", "வயிறு"])
                
                # Only provide summary if we have sufficient details
                if has_duration and has_severity and has_location:
                    summary = await self.generate_doctor_summary()
                    closure_message = "உங்க symptoms பத்தி நான் senior doctor-கிட்ட சொல்லி வைக்கறேன். அவங்க உங்களை பார்த்து proper treatment கொடுப்பாங்க. கவலைப்படாதீங்க, நாங்க உங்களுக்கு help பண்றோம். எல்லாம் சரியாகும்."
                    
                    logger.info("Generated doctor summary", extra={
                        "summary_length": len(summary),
                        "has_duration": has_duration,
                        "has_severity": has_severity,
                        "has_location": has_location
                    })
                    
                    return closure_message
            
            # Generate response
            response = self.model.generate_content(conversation_text)
            
            if response.text:
                ai_response = response.text.strip()
                
                # Clean the response to remove any leaked instructions
                ai_response = self._clean_llm_output(ai_response)
                
                # Limit questions to maximum 2 per response
                ai_response = self._limit_questions(ai_response)
                
                # Add AI response to conversation history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": ai_response
                })
                
                logger.info("Gemini chat completed", extra={
                    "response_length": len(ai_response)
                })
                return ai_response
            else:
                raise Exception("No response generated from Gemini")
                
        except Exception as error:
            logger.error(f"Gemini chat failed: {str(error)}")
            
            # Provide fallback response based on language
            if language == "ta" or "tamil" in language.lower():
                return "மன்னிக்கவும், எனக்கு இப்போது பதில் சொல்ல முடியவில்லை. மீண்டும் முயற்சி செய்யுங்கள்."
            else:
                return "Sorry, I'm having trouble responding right now. Please try again."
    
    def _create_system_prompt(self, language: str) -> str:
        """Create system prompt based on detected language"""
        return """You are a caring junior doctor doing pre-screening for patients. You speak naturally in Tamil mixed with English medical terms. Your role is to systematically gather information, comfort patients, and prepare a summary for the senior doctor.

        Your responsibilities:
        - REMEMBER what the patient has already told you - don't repeat the same questions
        - Ask progressive investigative questions to build a complete picture
        - Ask maximum 2 NEW questions per response based on what you don't know yet
        - Only greet with "வணக்கம்" in your VERY FIRST response, NEVER repeat greetings
        - When providing final summary and referral, DO NOT ask any more questions - just give closure message

Investigation sequence:
1. First: Acknowledge their problem, ask about onset and severity
2. Then: Ask about location, triggers, what makes it better/worse
3. Finally: Ask about associated symptoms, previous treatments
4. Complete: Provide summary and refer to senior doctor

Language style:
- Use Tamil script for Tamil words: எப்படி, இருக்கு, வாங்க, சரி
- Use English for medical terms: fever, medicine, blood pressure, symptoms
- Mix naturally: "Pain எங்க exactly இருக்கு?", "Medicine சாப்ட்டீங்களா?"
- Be warm and caring but don't repeat greetings

Examples:
Patient: "I have leg pain"
You: "வணக்கம், கவலைப்படாதீங்க. Leg pain எப்போ start ஆச்சு? Pain எவ்வளவு severe-ஆ இருக்கு (1-10)?"

Patient: "Started 2 days ago, very severe 9/10"
You: "சரி, ரெண்டு நாளா 9/10 pain. Pain எங்க exactly இருக்கு leg-ல? Walking பண்றப்போ அதிகமா வலிக்குதா?"

Patient: "In my calf muscle, worse when walking"
You: "Calf muscle-ல pain, walking பண்றப்போ அதிகம். வேற ஏதாவது symptoms இருக்கா? Swelling அல்லது numbness?"

Patient: "No other symptoms"
You: "சரி, calf muscle pain, walking-ல அதிகம், வேற symptoms இல்ல. Previous-ஆ ஏதாவது medicine சாப்ட்டீங்களா? இந்த pain-க்கு முன்னாடி ஏதாவது injury ஆச்சா?"

After gathering enough info: "உங்க symptoms பத்தி நான் senior doctor-கிட்ட சொல்லி வைக்கறேன். அவங்க உங்களை பார்த்து proper treatment கொடுப்பாங்க. கவலைப்படாதீங்க, நாங்க உங்களுக்கு help பண்றோம்."

Respond only with your junior doctor reply, nothing else."""
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        logger.info("Gemini conversation history reset")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get conversation statistics"""
        return {
            "message_count": len(self.conversation_history),
            "user_messages": len([msg for msg in self.conversation_history if msg["role"] == "user"]),
            "ai_messages": len([msg for msg in self.conversation_history if msg["role"] == "assistant"])
        }
    
    async def generate_doctor_summary(self) -> str:
        """Generate a summary for the senior doctor"""
        if not self.conversation_history:
            return "No conversation history available."
        
        # Extract patient messages
        patient_messages = [msg["content"] for msg in self.conversation_history if msg["role"] == "user"]
        
        if not patient_messages:
            return "No patient information gathered."
        
        summary_prompt = f"""Based on this conversation with a patient, create a brief medical summary for the senior doctor:

Patient conversation:
{' | '.join(patient_messages)}

Create a summary in this format:
- Chief complaint: [main symptoms/concerns]
- Duration: [when symptoms started]
- Severity: [mild/moderate/severe if mentioned]
- Associated symptoms: [other symptoms mentioned]
- Patient concerns: [any worries expressed]
- Recommended action: [urgent/routine consultation]

Keep it professional and concise."""

        try:
            response = self.model.generate_content(summary_prompt)
            if response.text:
                return response.text.strip()
            else:
                return "Unable to generate summary."
        except Exception as e:
            logger.error(f"Failed to generate doctor summary: {str(e)}")
            return "Summary generation failed."
    
    def _clean_llm_output(self, text: str) -> str:
        """
        Clean LLM output to remove any leaked instructions or meta-text
        """
        import re
        
        # Remove instruction patterns that might leak
        cleanup_patterns = [
            r"you are.*?doctor.*?patient",
            r"respond.*?like.*?doctor",
            r"use tamil.*?english",
            r"examples?:",
            r"patient:",
            r"you:",
            r"dr\.?\s*tamil:",
            r"assistant:",
            r"respond only with",
            r"output only",
            r"translation:",
            r"tamil translation:",
            r"here.*?translation",
            r"the translation is",
        ]
        
        cleaned_text = text
        
        # Remove patterns case-insensitively
        for pattern in cleanup_patterns:
            cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE)
        
        # Remove any lines that start with instruction-like text
        lines = cleaned_text.split('\n')
        clean_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip lines that look like instructions or examples
            skip_line = False
            instruction_indicators = [
                'respond', 'use tamil', 'use english', 'examples', 'guidelines', 
                'style', 'avoid', 'personality', 'role', 'conversation', 'language mixing'
            ]
            
            for indicator in instruction_indicators:
                if indicator in line.lower():
                    skip_line = True
                    break
            
            # Skip lines that start with formatting characters
            if line.startswith(('*', '-', '•', '1.', '2.', '3.')):
                skip_line = True
            
            if not skip_line:
                clean_lines.append(line)
        
        # Join clean lines
        if clean_lines:
            cleaned_text = ' '.join(clean_lines)
        else:
            cleaned_text = text  # Fallback to original if everything was filtered
        
        # Final cleanup
        cleaned_text = cleaned_text.strip(":- \"'\n\t ")
        
        return cleaned_text
    
    def _limit_questions(self, text: str) -> str:
        """
        Limit questions to maximum 2 per response
        """
        import re
        
        # Split by sentence endings but preserve the original structure
        parts = re.split(r'([.!।])', text)
        
        result_parts = []
        question_count = 0
        
        i = 0
        while i < len(parts):
            part = parts[i].strip()
            
            if not part:
                i += 1
                continue
            
            # Check if this part contains a question
            if '?' in part:
                if question_count < 2:
                    result_parts.append(part)
                    question_count += 1
                # Skip this question if we already have 2
            else:
                # Add statements and punctuation
                result_parts.append(part)
                # Add punctuation if it exists
                if i + 1 < len(parts) and parts[i + 1] in '.!।':
                    result_parts.append(parts[i + 1])
                    i += 1
            
            i += 1
        
        # Join and clean up
        result = ''.join(result_parts)
        
        # Clean up extra spaces and punctuation
        result = re.sub(r'\s+', ' ', result)
        result = re.sub(r'\s*([.!।])\s*', r'\1 ', result)
        
        return result.strip()
