# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Adaptive Music Therapy System — an AI-powered backend that detects a user's emotional state (via webcam or text) and dynamically transforms music (tempo, instrumentation, intensity) in near real-time. Target users are elderly individuals. Frontend is developed separately.

## Architecture

```
User Input (webcam/text)
    ↓
Mood Detection Service  →  getUserMood() → "sad" | "anxious" | "happy" | "calm"
    ↓
Backend API (Flask)     →  /api/mood, /api/music/transform, /api/music/stream
    ↓
Music Transform Service →  transformMusic(audio, mood) → modified_audio
    ↓
Frontend (separate repo)
```

**Core components:**

| Component | Location | Responsibility |
|---|---|---|
| Flask app factory | `app/__init__.py` | App init, CORS, blueprints |
| Mood routes | `app/routes/mood.py` | POST /api/mood |
| Music routes | `app/routes/music.py` | POST /api/music/transform, GET /api/music/stream |
| Mood detection | `app/services/mood_detection.py` | Gemini Vision / DeepFace / sentiment fallback |
| Music transform | `app/services/music_transform.py` | librosa/pydub transformations per mood |
| Schemas | `app/models/schemas.py` | Request/response dataclasses |

## Commands

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run dev server
cd backend && python run.py

# Run with environment variables
cd backend && cp .env.example .env  # then fill in keys
python run.py

# Run tests
cd backend && pytest tests/

# Run single test
cd backend && pytest tests/test_mood.py::test_getUserMood_returns_valid_mood -v
```

## Environment Variables

See `backend/.env.example`. Required:
- `GEMINI_API_KEY` — for Gemini Vision mood detection
- `FLASK_ENV` — `development` or `production`

## Mood-to-Music Mapping

| Mood | Tempo Change | Instrumentation |
|---|---|---|
| `sad` | -20% BPM | +piano layer, soft strings |
| `anxious` | -15% BPM | +ambient/drone, steady rhythm |
| `happy` | +10% BPM | brighter tones, no change needed |
| `calm` | no change | minimal transformation |

Fallback: if mood detection fails → default to `"calm"`.

## API Contract

```
POST /api/mood
  Body: { "image_base64": "..." } OR { "text": "..." }
  Response: { "mood": "calm", "confidence": 0.87 }

POST /api/music/transform
  Body: { "mood": "sad", "track_id": "default" }
  Response: { "audio_url": "/api/music/stream/<session_id>" }

GET /api/music/stream/<session_id>
  Response: audio/mpeg stream
```

## Key Constraints

- End-to-end latency < 3 seconds
- Never store facial image data — process in memory only, discard immediately
- Always inform user when AI is making decisions (the frontend handles display)
- If any service fails, return a pre-processed calming track (`audio/fallback/calm_default.mp3`)
