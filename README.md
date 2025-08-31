# Tamil Voice Gateway - Python Edition

A high-performance, real-time Tamil/English voice processing API built with FastAPI. Supports speech-to-text, text-to-speech, and translation with multiple provider options.

## 🚀 Quick Start

1. **Clone and navigate to the project:**
   ```bash
   cd tamil-voice-gateway-python
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start the server:**
   ```bash
   python3 start_server.py
   ```

4. **Access the application:**
   - Web UI: http://localhost:8000/static/
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health/

## 🎯 Features

### Real-Time Conversation APIs
- **`/v1/listen`** - Convert Tamil/English audio to English transcript
- **`/v1/speak`** - Convert English text to Tamil/English audio
- **`/v1/speak/preview`** - Get audio as base64 JSON response

### Multi-Provider Support
- **STT**: Sarvam AI (primary), Google Cloud STT (fallback)
- **TTS**: ElevenLabs with Tamil and English voices
- **Translation**: Google Cloud Translation

### Advanced Features
- JWT authentication for secure API access
- Rate limiting and request logging
- Dynamic provider switching
- Mixed language support (Tamil/English code-switching)
- Real-time audio streaming
- Comprehensive error handling

## 📁 Project Structure

```
tamil-voice-gateway-python/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── core/
│   │   ├── config.py          # Configuration management
│   │   └── logging.py         # Logging setup
│   ├── models/
│   │   ├── stt.py             # STT data models
│   │   ├── tts.py             # TTS data models
│   │   └── translation.py     # Translation models
│   ├── adapters/
│   │   ├── base.py            # Base adapter classes
│   │   ├── sarvam_stt.py      # Sarvam AI STT
│   │   ├── google_stt.py      # Google Cloud STT
│   │   ├── google_translate.py # Google Translation
│   │   └── elevenlabs_tts.py  # ElevenLabs TTS
│   ├── api/routes/
│   │   ├── health.py          # Health check endpoints
│   │   └── conversation.py    # Main conversation APIs
│   └── middleware/
│       ├── auth.py            # JWT authentication
│       └── rate_limit.py      # Rate limiting
├── static/
│   └── index.html             # Web UI for testing
├── requirements.txt           # Python dependencies
├── start_server.py           # Server startup script
├── simple_test.py            # Structure validation
└── test_apis.py              # API testing script
```

## 🔧 API Usage

### Authentication
All `/v1/*` endpoints require JWT authentication:
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -X POST http://localhost:8000/v1/listen
```

### Listen API (STT + Translation)
```bash
curl -X POST "http://localhost:8000/v1/listen" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "audio=@audio.wav" \
     -F "stt_provider=sarvam" \
     -F "timestamps=false"
```

### Speak API (Translation + TTS)
```bash
curl -X POST "http://localhost:8000/v1/speak" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "english_text": "Hello, how are you?",
       "target_language": "ta",
       "voice_speed": 1.0,
       "voice_provider": "elevenlabs"
     }'
```

## 🔑 Environment Configuration

Required environment variables in `.env`:

```bash
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true

# JWT
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=./gcp-key.json
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_TRANSLATE_PROJECT_ID=your-project-id

# ElevenLabs
ELEVENLABS_API_KEY=your-elevenlabs-key
ELEVENLABS_VOICE_ID_TA=tamil-voice-id
ELEVENLABS_VOICE_ID_EN=english-voice-id

# Sarvam AI
SARVAM_API_KEY=your-sarvam-key
```

## 🧪 Testing

### Quick Structure Test
```bash
python3 simple_test.py
```

### Full API Test
```bash
python3 test_apis.py
```

### Web UI Test
1. Open http://localhost:8000/static/
2. Click "Generate Test Token"
3. Test both Listen and Speak modules

## 🔄 Migration from TypeScript

This Python version provides equivalent functionality to the original TypeScript implementation:

| TypeScript | Python | Status |
|------------|--------|--------|
| Express.js | FastAPI | ✅ Complete |
| Node.js adapters | Python adapters | ✅ Complete |
| JWT middleware | JWT dependencies | ✅ Complete |
| Rate limiting | Custom middleware | ✅ Complete |
| Web UI | Static files | ✅ Complete |
| Real-time APIs | Async endpoints | ✅ Complete |

## 🚀 Performance Benefits

- **Async/Await**: Full async support with FastAPI
- **Type Safety**: Pydantic models for request/response validation
- **Auto Documentation**: OpenAPI/Swagger docs at `/docs`
- **Streaming**: Direct audio streaming without base64 encoding
- **Error Handling**: Comprehensive error responses
- **Logging**: Structured JSON logging

## 🛠️ Development

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run in Development Mode
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Add New Providers
1. Create adapter in `app/adapters/`
2. Extend base classes from `app/adapters/base.py`
3. Update models in `app/models/`
4. Add provider option to conversation routes

## 📊 Monitoring

- Health checks: `/health/` and `/health/detailed`
- Request logging with processing times
- Rate limit headers in responses
- Error tracking with structured logs

## 🔒 Security

- JWT authentication for protected endpoints
- Rate limiting per IP address
- Input validation with Pydantic
- Secure environment variable handling
- CORS configuration for production

## 📝 License

Same as original TypeScript version - MIT License

---

**🎉 The Python conversion is complete!** This implementation provides all the functionality of the original TypeScript version with improved performance, better type safety, and easier model switching capabilities.
