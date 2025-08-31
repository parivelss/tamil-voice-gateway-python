"""
Logging configuration for Tamil Voice Gateway
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """JSON log formatter"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields if present
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
            
        if hasattr(record, 'endpoint'):
            log_entry["endpoint"] = record.endpoint
            
        if hasattr(record, 'processing_time'):
            log_entry["processing_time"] = record.processing_time
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)


class PlainFormatter(logging.Formatter):
    """Plain text log formatter"""
    
    def __init__(self):
        super().__init__(
            fmt="[%(asctime)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )


def setup_logging():
    """Setup application logging"""
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Set formatter based on configuration
    if settings.LOG_FORMAT.lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = PlainFormatter()
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get logger with name"""
    return logging.getLogger(name)


def log_request(logger: logging.Logger, request_id: str, endpoint: str, **kwargs):
    """Log request with structured data"""
    extra = {
        "request_id": request_id,
        "endpoint": endpoint,
        **kwargs
    }
    
    logger.info("Request started", extra=extra)


def log_response(logger: logging.Logger, request_id: str, endpoint: str, 
                processing_time: float, status_code: int, **kwargs):
    """Log response with structured data"""
    extra = {
        "request_id": request_id,
        "endpoint": endpoint,
        "processing_time": processing_time,
        "status_code": status_code,
        **kwargs
    }
    
    if status_code >= 400:
        logger.error("Request failed", extra=extra)
    else:
        logger.info("Request completed", extra=extra)
