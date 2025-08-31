"""
Gemini Translation Adapter for Colloquial Tamil
"""

import logging
import google.generativeai as genai
from typing import Optional

from app.core.config import settings
from app.models.translation import TranslationResult

logger = logging.getLogger(__name__)


class GeminiTranslateAdapter:
    """Gemini-based translation adapter for colloquial Tamil"""
    
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    async def translate_to_colloquial_tamil(self, english_text: str) -> str:
        """
        Translate English text to colloquial Tamil using Gemini
        
        Args:
            english_text: English text to translate
            
        Returns:
            Colloquial Tamil translation
        """
        try:
            logger.info("Starting Gemini colloquial Tamil translation", extra={
                "text_length": len(english_text)
            })
            
            prompt = f"""You are a caring junior doctor translating for a patient. Translate this to natural, colloquial Tamil with a respectful and comforting tone.

Guidelines:
- Keep English medical terms as they are: fever, medicine, blood pressure, diabetes, etc.
- Use Tamil script for Tamil words: வணக்கம், எப்படி, இருக்கு, சாப்பிடு
- Mix naturally like real Tamil doctors: "Medicine சாப்ட்டு rest எடுங்க"
- Be respectful and comforting in tone
- For questions: sound caring and gentle
- For long explanations: be detailed but warm and reassuring
- Maintain the same meaning but make it sound like a caring doctor

Text to translate: "{english_text}"

Provide only the Tamil translation with caring doctor tone:"""

            response = self.model.generate_content(prompt)
            
            if response.text:
                tamil_text = response.text.strip()
                
                # Remove any translation instructions that might have leaked through
                tamil_text = self._clean_translation_output(tamil_text)
                
                logger.info("Gemini colloquial translation completed", extra={
                    "original_length": len(english_text),
                    "translated_length": len(tamil_text)
                })
                
                return tamil_text
            else:
                raise Exception("No translation generated from Gemini")
                
        except Exception as error:
            logger.error(f"Gemini translation failed: {str(error)}")
            # Fallback to original text if translation fails
            return english_text
    
    async def translate(self, text: str, target_language: str, source_language: str = "auto") -> TranslationResult:
        """
        Generic translation method for compatibility
        """
        if target_language == "ta":
            translated_text = await self.translate_to_colloquial_tamil(text)
        else:
            # For non-Tamil targets, use a simpler approach
            translated_text = text
            
        return TranslationResult(
            text=translated_text,
            source_language=source_language,
            target_language=target_language,
            confidence=0.95
        )
    
    async def detect_language(self, text: str) -> str:
        """
        Simple language detection
        """
        # Simple heuristic - if contains Tamil script, it's Tamil
        if any('\u0b80' <= char <= '\u0bff' for char in text):
            return "ta"
        else:
            return "en"
    
    def _clean_translation_output(self, text: str) -> str:
        """
        Clean up translation output to remove any leaked instructions
        """
        # Remove common instruction phrases that might leak through
        cleanup_patterns = [
            "translate this to",
            "translation:",
            "in tamil:",
            "colloquial tamil:",
            "natural tamil:",
            "doctor would say:",
            "translate to colloquial",
            "output only the tamil translation:",
            "text:",
            "tamil translation:",
            "அன்றாடப் பேச்சுத் தமிழுக்கு",
            "மொழிபெயர்க்கவும்",
            "here is the translation:",
            "here's the translation:",
            "the translation is:",
            "tamil:"
        ]
        
        cleaned_text = text
        
        # Remove instruction patterns
        for pattern in cleanup_patterns:
            # Case insensitive removal
            import re
            cleaned_text = re.sub(re.escape(pattern), "", cleaned_text, flags=re.IGNORECASE)
        
        # Remove any leading/trailing colons, dashes, quotes, or whitespace
        cleaned_text = cleaned_text.strip(":- \"'\n\t ")
        
        # Remove any lines that look like instructions
        lines = cleaned_text.split('\n')
        clean_lines = []
        for line in lines:
            line = line.strip()
            # Skip lines that look like instructions
            if any(word in line.lower() for word in ['translate', 'output', 'respond', 'guidelines', 'style']):
                continue
            if line and not line.startswith('*') and not line.startswith('-'):
                clean_lines.append(line)
        
        if clean_lines:
            cleaned_text = ' '.join(clean_lines)
        
        return cleaned_text.strip()
