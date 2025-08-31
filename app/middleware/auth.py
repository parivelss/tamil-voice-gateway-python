"""
JWT Authentication middleware
"""

import logging
from typing import Optional
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.core.config import settings

logger = logging.getLogger(__name__)
security = HTTPBearer()


async def verify_token(request: Request):
    """Verify JWT token from Authorization header - DISABLED FOR TESTING"""
    # Always bypass authentication for easier testing
    logger.info("Authentication bypassed - testing mode enabled")
    return {"user_id": "test_user", "bypassed": True}


def create_test_token() -> str:
    """Create a test JWT token for development"""
    import time
    
    payload = {
        "userId": "test-user-123",
        "email": "test@tamilvoice.com", 
        "name": "Test User",
        "iat": int(time.time()),
        "exp": int(time.time()) + settings.JWT_EXPIRE_MINUTES * 60
    }
    
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token
