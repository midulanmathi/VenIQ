# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Crowd-Aware DJ System — a real-time venue assistant that watches a crowd through a webcam, uses Gemini Vision to describe the scene and score its energy, and automatically recommends the next Spotify track when the vibe shifts. A DJ interface shows the current recommendation and allows manual override.

This is not a music transformation tool — it selects existing Spotify tracks. No audio processing.

## User Flow

```
1. Browser webcam captures a frame every 10 seconds
2. Frontend sends frame → POST /api/crowd/analyze
3. Gemini Vision describes the crowd: energy score (1–10) + sentiment label
4. Backend compares new energy to previous:
     - delta < 2 and same sentiment → return { "changed": false }
     - delta >= 2 OR new sentiment → fetch Spotify recommendations → return new track
5. Frontend auto-queues the track; DJ can override via POST /api/playback/override
6. DJ sees: current track, crowd description, energy level
```

## Architecture

```
Browser webcam (every 10s)
    ↓  POST /api/crowd/analyze
Gemini Vision → { description, energy: 1–10, sentiment }
    ↓
Change Detection (energy delta >= 2 OR sentiment changed)
    ↓
Spotify Recommendations API → track list
    ↓
{ changed, energy, description, sentiment, track }
    ↓
Frontend DJ interface (separate repo)
```

**Core components:**

| Component | Location | Responsibility |
|---|---|---|
| Flask app factory | `app/__init__.py` | App init, CORS, blueprints |
| Crowd route | `app/routes/crowd.py` | POST /api/crowd/analyze — full pipeline |
| Playback route | `app/routes/playback.py` | GET /api/playback/current, POST /api/playback/override |
| Crowd service | `app/services/crowd.py` | Gemini Vision → scene description + energy + sentiment |
| Spotify service | `app/services/spotify.py` | Client credentials auth + recommendations |
| Schemas | `app/models/schemas.py` | Dataclasses for SceneResult, Track, CrowdAnalyzeResponse |

## Commands

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run dev server
cd backend && python run.py

# Set up environment
cd backend && cp .env.example .env  # fill in all three keys

# Run tests
cd backend && pytest tests/

# Run single test
cd backend && pytest tests/test_crowd.py -v
```

## Environment Variables

See `backend/.env.example`. All three are required:
- `GEMINI_API_KEY` — Gemini Vision crowd analysis
- `SPOTIFY_CLIENT_ID` — Spotify developer app (client credentials, no user OAuth)
- `SPOTIFY_CLIENT_SECRET` — Spotify developer app

Get Spotify keys at: https://developer.spotify.com/dashboard (free, create an app)

## API Contract

```
POST /api/crowd/analyze
  Body:    { "image_base64": "<base64 JPEG>" }
  No change: { "changed": false, "energy": 5, "description": "..." }
  Changed:   { "changed": true, "energy": 8, "description": "...", "sentiment": "party",
               "track": { "name": "...", "artist": "...", "uri": "spotify:track:...",
                          "preview_url": "...", "spotify_url": "..." } }

GET /api/playback/current
  Response:  { "track": {...} | null, "source": "auto" | "override" | null }

POST /api/playback/override
  Body (option A): { "track": { "name": "...", "uri": "...", ... } }
  Body (option B): { "sentiment": "party" }   ← fetches a fresh recommendation
  Response:  { "track": {...}, "source": "override" }
```

## Sentiment → Spotify Mapping

| Sentiment | Seed Genres | Energy | Tempo |
|---|---|---|---|
| `study` | classical, ambient | 0.25 | 70 BPM |
| `chill` | chill, indie | 0.40 | 90 BPM |
| `calm` | classical, sleep | 0.20 | 65 BPM |
| `party` | pop, dance, hip-hop | 0.85 | 128 BPM |
| `intense` | rock, electronic | 0.90 | 140 BPM |
| `romantic` | jazz, soul, r-n-b | 0.35 | 80 BPM |

## Key Constraints

- Never store webcam frames — process base64 in memory only, discard after Gemini responds
- Spotify uses **Client Credentials** (app-level) — no per-user login required
- Change detection threshold is configurable via `Config.ENERGY_CHANGE_THRESHOLD` (default: 2)
- Both energy delta AND sentiment change can trigger a new recommendation independently
- Crowd state (`_state`) and playback state (`_current`) are in-memory — reset on server restart
