"""
Rate limiting middleware
"""

import logging
import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using in-memory storage"""
    
    def __init__(self, app):
        super().__init__(app)
        self.requests: Dict[str, Tuple[int, float]] = {}  # {client_ip: (count, window_start)}
        self.max_requests = settings.RATE_LIMIT_REQUESTS
        self.window_seconds = settings.RATE_LIMIT_WINDOW
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        
        # Skip rate limiting for health checks
        if request.url.path.startswith("/health"):
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Clean up old entries
        self._cleanup_old_entries(current_time)
        
        # Check rate limit
        if self._is_rate_limited(client_ip, current_time):
            logger.warning(f"Rate limit exceeded for {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": str(self.window_seconds)}
            )
        
        # Update request count
        self._update_request_count(client_ip, current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = max(0, self.max_requests - self.requests[client_ip][0])
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(self.requests[client_ip][1] + self.window_seconds))
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"
    
    def _is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """Check if client is rate limited"""
        if client_ip not in self.requests:
            return False
        
        count, window_start = self.requests[client_ip]
        
        # Check if we're still in the same window
        if current_time - window_start < self.window_seconds:
            return count >= self.max_requests
        
        return False
    
    def _update_request_count(self, client_ip: str, current_time: float):
        """Update request count for client"""
        if client_ip not in self.requests:
            self.requests[client_ip] = (1, current_time)
            return
        
        count, window_start = self.requests[client_ip]
        
        # Check if we need to start a new window
        if current_time - window_start >= self.window_seconds:
            self.requests[client_ip] = (1, current_time)
        else:
            self.requests[client_ip] = (count + 1, window_start)
    
    def _cleanup_old_entries(self, current_time: float):
        """Remove old entries to prevent memory leaks"""
        expired_ips = [
            ip for ip, (_, window_start) in self.requests.items()
            if current_time - window_start > self.window_seconds * 2
        ]
        
        for ip in expired_ips:
            del self.requests[ip]
