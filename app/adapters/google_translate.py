"""
Google Cloud Translation Adapter
"""

import logging
from typing import Optional
from google.cloud import translate_v2 as translate

from app.core.config import settings
from app.models.translation import TranslationResult, LanguageDetectionResult
from app.adapters.base import TranslationAdapter

logger = logging.getLogger(__name__)


class GoogleTranslateAdapter(TranslationAdapter):
    """Google Cloud Translation adapter"""
    
    def __init__(self):
        self.client = translate.Client()
        self.project_id = settings.GOOGLE_TRANSLATE_PROJECT_ID
    
    async def translate(self, text: str, target_language: str, source_language: str = "auto") -> TranslationResult:
        """
        Translate text between languages with colloquial style for Tamil
        
        Args:
            text: Text to translate
            target_language: Target language code (e.g., 'ta', 'en')
            source_language: Source language code (default: 'auto')
            
        Returns:
            TranslationResult with translated text and metadata
        """
        try:
            # Validate target language
            valid_languages = ["ta", "en", "hi", "bn", "gu", "kn", "ml", "mr", "or", "pa", "te"]
            if target_language not in valid_languages:
                raise ValueError(f"Unsupported target language: {target_language}")
            
            logger.info("Starting translation", extra={
                "source": source_language,
                "target": target_language,
                "text_length": len(text)
            })
            
            # Map to Google Translate language codes
            source_code = self._map_language_code(source_language)
            target_code = self._map_language_code(target_language)
            
            # For Tamil translations, use colloquial style
            translation_text = self._prepare_colloquial_translation(text, target_language)
            
            # Perform translation
            result = self.client.translate(
                translation_text,
                target_language=target_code,
                source_language=source_code if source_language != "auto" else None
            )
            translated_text = result['translatedText']
            # Decode HTML entities (e.g., &#39; -> ')
            import html
            translated_text = html.unescape(translated_text)
            
            # Clean up colloquial prompt from translated text if present
            if target_language == "ta" and translation_text != text:
                translated_text = self._clean_colloquial_prompt(translated_text, text)
            detected_source = result.get('detectedSourceLanguage', source_language or 'unknown')
            
            translation_result = TranslationResult(
                text=translated_text,
                source_language=detected_source,
                target_language=target_language,
                confidence=1.0,  # Google doesn't provide confidence scores
                provider="google"
            )
            
            logger.info("Google translation completed", extra={
                "source_lang": detected_source,
                "target_lang": target_language,
                "original_length": len(text),
                "translated_length": len(translated_text)
            })
            
            return translation_result
            
        except Exception as error:
            logger.error(f"Google translation failed: {str(error)}")
            raise Exception(f"Google translation failed: {str(error)}")
    
    async def detect_language(self, text: str) -> str:
        """
        Detect language of text using Google Cloud Translation
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected language code
        """
        try:
            logger.info("Starting Google language detection", extra={
                "text_length": len(text)
            })
            
            result = self.client.detect_language(text)
            
            detected_language = result['language']
            confidence = result['confidence']
            
            logger.info("Google language detection completed", extra={
                "detected_language": detected_language,
                "confidence": confidence
            })
            
            return detected_language
            
        except Exception as error:
            logger.error(f"Google language detection failed: {str(error)}")
            raise Exception(f"Google language detection failed: {str(error)}")
    
    async def translate_to_english(self, text: str, source_language: Optional[str] = None) -> str:
        """
        Translate text to English
        
        Args:
            text: Text to translate
            source_language: Source language code (optional, will auto-detect if not provided)
            
        Returns:
            Translated text in English
        """
        try:
            logger.info("Starting translation to English", extra={
                "text_length": len(text),
                "source_language": source_language
            })
            
            # If no source language specified, detect it first
            if not source_language or source_language == "auto":
                try:
                    detection_result = await self.detect_language(text)
                    detected_lang = detection_result.language
                    
                    # If detected language is English, no translation needed
                    if detected_lang == 'en':
                        logger.info("Text is already in English, no translation needed")
                        return text
                    
                    source_language = detected_lang
                except Exception:
                    # If detection fails, proceed with translation anyway
                    source_language = None
            
            # If source language is English, return as-is
            if source_language == 'en':
                logger.info("Source language is English, no translation needed")
                return text
            
            # Make translation request - use the working API call pattern
            result = self.client.translate(text, target_language='en')
            
            translated_text = result['translatedText']
            detected_language = result.get('detectedSourceLanguage', source_language)
            
            logger.info("Translation completed", extra={
                "detected_language": detected_language,
                "translated_length": len(translated_text)
            })
            
            return translated_text
            
        except Exception as error:
            logger.error(f"Google translation failed: {str(error)}")
            # Return original text if translation fails
            return text
    
    async def translate_to_tamil(self, text: str, source_language: Optional[str] = None) -> TranslationResult:
        """Convenience method to translate to Tamil"""
        return await self.translate(text, "ta", source_language)
    
    def _prepare_colloquial_translation(self, text: str, target_language: str) -> str:
        """
        Prepare text for colloquial translation, especially for Tamil
        
        Args:
            text: Original text to translate
            target_language: Target language code
            
        Returns:
            Modified text with colloquial context if needed
        """
        if target_language == "ta":
            # Add specific context for colloquial Tamil
            colloquial_prompt = (
                "Translate to everyday spoken Tamil (not formal literary Tamil). "
                "Use casual, conversational words that people actually speak in daily life: "
            )
            return f"{colloquial_prompt}{text}"
        
        return text
    
    def _map_language_code(self, language: str) -> str:
        """Map language code to Google Translate format"""
        if language == "auto":
            return None  # Let Google auto-detect
        
        language_map = {
            "ta": "ta",
            "en": "en", 
            "hi": "hi",
            "bn": "bn",
            "gu": "gu",
            "kn": "kn",
            "ml": "ml",
            "mr": "mr",
            "or": "or",
            "pa": "pa",
            "te": "te"
        }
        
        return language_map.get(language, "en")
    
    def _clean_colloquial_prompt(self, translated_text: str, original_text: str) -> str:
        """
        Remove colloquial prompt instructions from translated text
        
        Args:
            translated_text: Full translated text including prompt
            original_text: Original English text to translate
            
        Returns:
            Clean translated text without prompt instructions
        """
        # Look for patterns that indicate the prompt was translated
        prompt_indicators = [
            "தினசரி பேசும் தமிழில் மொழிபெயர்க்கவும்",
            "சாதாரண பேச்சு தமிழில்",
            "முறையான இலக்கிய தமிழ் அல்ல",
            "translate to everyday spoken tamil",
            "use casual, conversational words"
        ]
        
        # Remove prompt-related text from the beginning
        cleaned_text = translated_text.strip()
        
        # Try to find where the actual translation starts
        # Look for common separators or the original text pattern
        lines = cleaned_text.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            # Skip lines that contain prompt indicators
            if any(indicator in line_lower for indicator in prompt_indicators):
                continue
            # Skip empty lines or lines with just punctuation
            if not line.strip() or line.strip() in [':', '-', '।']:
                continue
            # This might be the start of actual translation
            if line.strip():
                cleaned_text = '\n'.join(lines[i:]).strip()
                break
        
        # If we still have prompt text, try to extract just the translation
        if len(cleaned_text) > len(original_text) * 3:  # Heuristic: if too long, likely contains prompt
            # Try to find the actual translation after common separators
            separators = [':', '।', '-', '\n']
            for sep in separators:
                if sep in cleaned_text:
                    parts = cleaned_text.split(sep)
                    # Take the last substantial part
                    for part in reversed(parts):
                        if part.strip() and len(part.strip()) > 3:
                            cleaned_text = part.strip()
                            break
                    break
        
        return cleaned_text
