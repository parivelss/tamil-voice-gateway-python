#!/usr/bin/env python3
"""
Start script for Tamil Voice Gateway Python server
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed"""
    try:
        import fastapi
        import uvicorn
        import pydantic
        import httpx
        print("✅ Core dependencies available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        return False

def install_dependencies():
    """Install dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "fastapi", "uvicorn[standard]", "python-multipart", 
            "pydantic", "pydantic-settings", "httpx", "python-dotenv",
            "requests", "aiofiles"
        ], check=True)
        print("✅ Core dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def check_env_file():
    """Check if .env file exists"""
    env_file = Path(".env")
    if env_file.exists():
        print("✅ Environment file found")
        return True
    else:
        print("❌ .env file not found")
        print("Please copy .env.example to .env and configure your API keys")
        return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Tamil Voice Gateway Python server...")
    
    try:
        # Import here to avoid issues if dependencies aren't installed
        import uvicorn
        
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("❌ FastAPI/Uvicorn not installed. Installing now...")
        if install_dependencies():
            import uvicorn
            uvicorn.run(
                "app.main:app",
                host="0.0.0.0", 
                port=8000,
                reload=True,
                log_level="info"
            )
        else:
            print("❌ Failed to start server")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    print("🎙️ Tamil Voice Gateway - Python Edition")
    print("=" * 50)
    
    # Check environment
    if not check_env_file():
        return
    
    # Check/install dependencies
    if not check_requirements():
        if not install_dependencies():
            return
    
    # Start server
    print("\n🌐 Server will be available at:")
    print("   • API: http://localhost:8000")
    print("   • Docs: http://localhost:8000/docs")
    print("   • Web UI: http://localhost:8000/static/")
    print("   • Health: http://localhost:8000/health/")
    print("\n📝 API Endpoints:")
    print("   • POST /v1/listen - Convert audio to English transcript")
    print("   • POST /v1/speak - Convert English text to Tamil/English audio")
    print("   • POST /v1/speak/preview - Get audio as base64 JSON")
    print("\n🔑 Note: /v1/* endpoints require JWT authentication")
    print("   Use the 'Generate Test Token' button in the web UI")
    print("\n⏹️  Press Ctrl+C to stop the server")
    print("=" * 50)
    
    start_server()

if __name__ == "__main__":
    main()
