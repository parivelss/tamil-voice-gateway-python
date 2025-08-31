#!/bin/bash

# Tamil Voice Gateway Python Server Startup Script
# This script sets the required environment variables and starts the server

echo "🚀 Starting Tamil Voice Gateway Python Server..."

# Set Google Cloud credentials path
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/gcp-key.json"

# Verify credentials file exists
if [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "❌ Error: Google Cloud credentials file not found at $GOOGLE_APPLICATION_CREDENTIALS"
    echo "Please ensure gcp-key.json exists in the project directory"
    exit 1
fi

echo "✅ Google Cloud credentials found: $GOOGLE_APPLICATION_CREDENTIALS"

# Start the server
echo "🌐 Starting server on http://localhost:8005"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
