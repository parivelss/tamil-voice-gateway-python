"""
Configuration management using Pydantic settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    DEBUG: bool = Field(default=True, description="Debug mode")
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format")
    
    # Offline mode for testing
    OFFLINE_MODE: bool = Field(default=False, description="Enable offline mode for testing")
    
    # OpenAI API configuration
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key for LLM")
    
    # Google API configuration
    GOOGLE_API_KEY: str = Field(default="", description="Google API key for Gemini")
    
    # JWT Configuration
    JWT_SECRET: str = Field(..., description="JWT secret key")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_EXPIRE_MINUTES: int = Field(default=1440, description="JWT expiration in minutes")
    
    # Google Cloud Configuration
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = Field(default=None, description="Path to Google service account key")
    GOOGLE_PROJECT_ID: str = Field(..., description="Google Cloud project ID")
    GOOGLE_STT_LANGUAGE: str = Field(default="ta-IN", description="Primary STT language")
    GOOGLE_STT_ALT_LANGS: str = Field(default="en-IN", description="Alternative STT languages")
    GOOGLE_TRANSLATE_PROJECT_ID: str = Field(..., description="Google Translate project ID")
    GOOGLE_TRANSLATE_LOCATION: str = Field(default="global", description="Google Translate location")
    
    # ElevenLabs Configuration
    ELEVENLABS_API_KEY: str = Field(..., description="ElevenLabs API key")
    ELEVENLABS_VOICE_ID_TA: Optional[str] = Field(default=None, description="Tamil voice ID")
    ELEVENLABS_VOICE_ID_EN: Optional[str] = Field(default=None, description="English voice ID")
    ELEVENLABS_TTS_MODEL: str = Field(default="eleven_multilingual_v2", description="ElevenLabs TTS model")
    
    # Sarvam AI Configuration
    SARVAM_API_KEY: Optional[str] = Field(default=None, description="Sarvam AI API key")
    
    # Default Providers
    DEFAULT_STT_PROVIDER: str = Field(default="sarvam", description="Default STT provider")
    DEFAULT_TTS_PROVIDER: str = Field(default="elevenlabs", description="Default TTS provider")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Rate limit requests per window")
    RATE_LIMIT_WINDOW: int = Field(default=60, description="Rate limit window in seconds")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Validate required settings
def validate_settings():
    """Validate critical settings"""
    errors = []
    
    if not settings.JWT_SECRET:
        errors.append("JWT_SECRET is required")
    
    if not settings.GOOGLE_PROJECT_ID:
        errors.append("GOOGLE_PROJECT_ID is required")
    
    if not settings.GOOGLE_TRANSLATE_PROJECT_ID:
        errors.append("GOOGLE_TRANSLATE_PROJECT_ID is required")
    
    if not settings.ELEVENLABS_API_KEY:
        errors.append("ELEVENLABS_API_KEY is required")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")

# Validate on import
try:
    validate_settings()
except ValueError as e:
    print(f"⚠️  Configuration warning: {e}")
    print("Some features may not work properly without proper configuration.")
