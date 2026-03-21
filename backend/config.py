import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB upload limit
    AUDIO_BASE_TRACKS_DIR = os.path.join(os.path.dirname(__file__), "audio", "base_tracks")
    AUDIO_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "audio", "output")
    FALLBACK_TRACK = os.path.join(os.path.dirname(__file__), "audio", "fallback", "calm_default.mp3")
    DEFAULT_MOOD = "calm"
