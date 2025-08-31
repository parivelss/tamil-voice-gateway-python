"""
Health check API routes
"""

import logging
import time
from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model"""
    ok: bool
    timestamp: int
    service: str
    version: str
    status: str


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        ok=True,
        timestamp=int(time.time() * 1000),
        service="tamil-voice-gateway-python",
        version="2.0.0",
        status="healthy"
    )


@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check with service status"""
    try:
        # TODO: Add actual service health checks here
        # - Database connectivity
        # - External API availability
        # - Resource usage
        
        return {
            "ok": True,
            "timestamp": int(time.time() * 1000),
            "service": "tamil-voice-gateway-python",
            "version": "2.0.0",
            "status": "healthy",
            "services": {
                "sarvam_stt": "available",
                "google_stt": "available", 
                "google_translate": "available",
                "elevenlabs_tts": "available"
            },
            "uptime": "unknown",  # TODO: Track actual uptime
            "memory_usage": "unknown"  # TODO: Add memory monitoring
        }
        
    except Exception as error:
        logger.error(f"Health check failed: {str(error)}")
        return {
            "ok": False,
            "timestamp": int(time.time() * 1000),
            "service": "tamil-voice-gateway-python",
            "version": "2.0.0",
            "status": "unhealthy",
            "error": str(error)
        }
