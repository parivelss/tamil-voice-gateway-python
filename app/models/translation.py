"""
Translation data models
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class TranslationProvider(str, Enum):
    """Available translation providers"""
    GOOGLE = "google"
    LIBRE = "libre"


class TranslationOptions(BaseModel):
    """Translation processing options"""
    provider: TranslationProvider = Field(default=TranslationProvider.GOOGLE, description="Translation provider")
    confidence_threshold: float = Field(default=0.8, description="Minimum confidence for translation")


class TranslationResult(BaseModel):
    """Translation result"""
    text: str = Field(description="Translated text")
    source_language: str = Field(description="Detected/specified source language")
    target_language: str = Field(description="Target language")
    confidence: float = Field(description="Translation confidence score")
    provider: Optional[str] = Field(default=None, description="Translation provider used")


class LanguageDetectionResult(BaseModel):
    """Language detection result"""
    language: str = Field(description="Detected language code")
    confidence: float = Field(description="Detection confidence score")
    provider: Optional[str] = Field(default=None, description="Provider used for detection")
