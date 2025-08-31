"""
Authentication routes for JWT token management
"""

import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt

from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


class TokenRequest(BaseModel):
    user_id: str
    expires_in: int = 3600


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


@router.post("/token", response_model=TokenResponse)
async def generate_token(request: TokenRequest):
    """Generate JWT token for authentication"""
    try:
        # Create token payload
        payload = {
            "user_id": request.user_id,
            "exp": datetime.utcnow() + timedelta(seconds=request.expires_in),
            "iat": datetime.utcnow()
        }
        
        # Generate token
        token = jwt.encode(
            payload,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        )
        
        logger.info("JWT token generated", extra={
            "user_id": request.user_id,
            "expires_in": request.expires_in
        })
        
        return TokenResponse(
            access_token=token,
            expires_in=request.expires_in
        )
        
    except Exception as error:
        logger.error(f"Token generation failed: {str(error)}")
        raise HTTPException(status_code=500, detail="Token generation failed")


@router.post("/verify")
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        logger.info("JWT token verified", extra={
            "user_id": payload.get("user_id")
        })
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as error:
        logger.error(f"Token verification failed: {str(error)}")
        raise HTTPException(status_code=401, detail="Token verification failed")
