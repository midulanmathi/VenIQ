from dataclasses import dataclass


@dataclass
class MoodResponse:
    mood: str        # "happy" | "sad" | "anxious" | "calm"
    confidence: float


@dataclass
class TransformRequest:
    mood: str
    track_id: str = "default"


@dataclass
class TransformResponse:
    session_id: str
    audio_url: str
