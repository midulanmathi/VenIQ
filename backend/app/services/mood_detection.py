"""
Mood Detection Service

Priority order:
1. Gemini Vision API (if image_base64 provided and GEMINI_API_KEY set)
2. Text sentiment (if text provided)
3. Fallback → "calm"

Returns: (mood: str, confidence: float)
Valid moods: "happy", "sad", "anxious", "calm"
"""

import base64
import os
from typing import Optional

VALID_MOODS = {"happy", "sad", "anxious", "calm"}
DEFAULT_MOOD = "calm"


def get_user_mood(
    image_b64: Optional[str] = None,
    text: Optional[str] = None,
) -> tuple[str, float]:
    """
    Determine user's current mood.

    Args:
        image_b64: base64-encoded JPEG/PNG from webcam (no facial data is stored)
        text:      freeform text input for sentiment fallback

    Returns:
        (mood, confidence) — mood is always a valid VALID_MOODS entry
    """
    try:
        if image_b64:
            return _detect_from_image(image_b64)
        if text:
            return _detect_from_text(text)
    except Exception:
        pass

    return DEFAULT_MOOD, 0.5


def _detect_from_image(image_b64: str) -> tuple[str, float]:
    """Use Gemini Vision to classify mood from a webcam frame."""
    import google.generativeai as genai

    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    image_bytes = base64.b64decode(image_b64)

    prompt = (
        "Look at this image of a person's face. "
        "Classify their emotional state as exactly one of: happy, sad, anxious, calm. "
        "Reply with JSON only: {\"mood\": \"<label>\", \"confidence\": <0.0-1.0>}"
    )

    response = model.generate_content(
        [{"mime_type": "image/jpeg", "data": image_bytes}, prompt]
    )

    import json
    result = json.loads(response.text.strip().strip("```json").strip("```"))
    mood = result.get("mood", DEFAULT_MOOD).lower()
    confidence = float(result.get("confidence", 0.7))

    if mood not in VALID_MOODS:
        mood = DEFAULT_MOOD

    # Image bytes are never written to disk — discarded here
    return mood, confidence


def _detect_from_text(text: str) -> tuple[str, float]:
    """Simple keyword-based sentiment → mood mapping (no external API needed)."""
    text_lower = text.lower()

    scores = {
        "sad": sum(w in text_lower for w in ["sad", "depressed", "lonely", "down", "cry", "hopeless", "grief"]),
        "anxious": sum(w in text_lower for w in ["anxious", "worried", "nervous", "scared", "panic", "stress", "afraid"]),
        "happy": sum(w in text_lower for w in ["happy", "joy", "great", "wonderful", "excited", "cheerful", "good"]),
        "calm": sum(w in text_lower for w in ["calm", "peaceful", "relaxed", "fine", "okay", "serene", "quiet"]),
    }

    best_mood = max(scores, key=lambda m: scores[m])
    total = sum(scores.values()) or 1
    confidence = scores[best_mood] / total

    if scores[best_mood] == 0:
        return DEFAULT_MOOD, 0.5

    return best_mood, min(confidence, 0.95)
