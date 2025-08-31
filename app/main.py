"""
Tamil Voice Gateway - Python FastAPI Implementation
Real-time conversation APIs for Tamil/English speech processing
"""

from fastapi import FastAPI, Request, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, JSONResponse
import uvicorn
import logging
import time
from contextlib import asynccontextmanager
from typing import Optional, Union
import io

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes import conversation, health, vaanga_pesalam, auth
from app.middleware.auth import verify_token
from app.middleware.rate_limit import RateLimitMiddleware

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Tamil Voice Gateway starting up...")
    logger.info(f"Server: {settings.HOST}:{settings.PORT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Default STT: {settings.DEFAULT_STT_PROVIDER}")
    logger.info(f"Default TTS: {settings.DEFAULT_TTS_PROVIDER}")
    
    yield
    
    logger.info("👋 Tamil Voice Gateway shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Tamil Voice Gateway",
    description="Real-time conversation APIs for Tamil/English speech processing",
    version="2.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Request logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all requests"""
    start_time = time.time()
    
    logger.info("Request started", extra={
        "method": request.method,
        "url": str(request.url),
        "client_ip": request.client.host if request.client else "unknown"
    })
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info("Request completed", extra={
        "method": request.method,
        "url": str(request.url),
        "status_code": response.status_code,
        "process_time": round(process_time, 3)
    })
    
    response.headers["X-Process-Time"] = str(round(process_time, 3))
    return response

# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", extra={
        "method": request.method,
        "url": str(request.url),
        "exception_type": type(exc).__name__
    })
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="static", html=True), name="static")
except RuntimeError:
    # Static directory doesn't exist yet
    logger.warning("Static directory not found, skipping static file mounting")

# Include routers
app.include_router(conversation.router, prefix="/v1", tags=["conversation"])
app.include_router(vaanga_pesalam.router, prefix="/v1", tags=["vaanga-pesalam"])
app.include_router(auth.router, prefix="/v1", tags=["authentication"])
app.include_router(health.router, prefix="/health", tags=["health"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "tamil-voice-gateway",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs" if settings.DEBUG else "disabled",
        "endpoints": {
            "listen": "POST /v1/listen - Audio → English transcript",
            "speak": "POST /v1/speak - English text → Target language audio",
            "health": "GET /health - Service health check"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
