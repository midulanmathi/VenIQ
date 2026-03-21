"""
Crowd Scene Analysis Service

Sends a webcam frame to Gemini Vision and returns a structured scene description:
  - description: human-readable text for display
  - energy:      1–10 scale (1=quiet/still, 10=highly energetic/chaotic)
  - sentiment:   one of: study | chill | calm | party | intense | romantic

This is the first step in the pipeline. The sentiment feeds directly into Spotify recommendations.
"""

import base64
import json
import os
from config import Config

VALID_SENTIMENTS = {"study", "chill", "calm", "party", "intense", "romantic"}
DEFAULT_SENTIMENT = "chill"
DEFAULT_ENERGY = 5


def describe_crowd(image_b64: str) -> dict:
    """
    Analyze a crowd/venue frame with Gemini Vision.

    Args:
        image_b64: base64-encoded JPEG frame from a webcam (never written to disk)

    Returns:
        {
            "description": "A lecture hall with students working quietly...",
            "energy": 3,
            "sentiment": "study"
        }
    Falls back to defaults if Gemini is unavailable.
    """
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return _fallback("GEMINI_API_KEY not set")

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        image_bytes = base64.b64decode(image_b64)

        prompt = (
            "You are analyzing a video frame from a venue or event space to help a DJ pick the right music.\n"
            "Describe the scene and determine the appropriate music sentiment.\n\n"
            "Reply with JSON only, no markdown:\n"
            '{"description": "<1-2 sentence description of venue and crowd>", '
            '"energy": <integer 1-10>, '
            '"sentiment": "<one of: study, chill, calm, party, intense, romantic>"}\n\n'
            "Guidelines:\n"
            "- energy 1-3: quiet, still, focused (libraries, empty rooms, study halls)\n"
            "- energy 4-6: moderate activity, conversation, casual gatherings\n"
            "- energy 7-10: high activity, dancing, cheering, crowded events\n"
            "- sentiment 'study': quiet focus, academic setting\n"
            "- sentiment 'chill': relaxed social atmosphere\n"
            "- sentiment 'calm': peaceful, low-key environment\n"
            "- sentiment 'party': dancing, celebration, nightlife\n"
            "- sentiment 'intense': high-energy concerts, sports, competitive events\n"
            "- sentiment 'romantic': intimate, dim lighting, couples"
        )

        response = model.generate_content(
            [{"mime_type": "image/jpeg", "data": image_bytes}, prompt]
        )

        raw = response.text.strip().strip("```json").strip("```").strip()
        result = json.loads(raw)

        energy = int(result.get("energy", DEFAULT_ENERGY))
        energy = max(1, min(10, energy))

        sentiment = result.get("sentiment", DEFAULT_SENTIMENT).lower()
        if sentiment not in VALID_SENTIMENTS:
            sentiment = DEFAULT_SENTIMENT

        return {
            "description": result.get("description", ""),
            "energy": energy,
            "sentiment": sentiment,
        }

    except Exception as e:
        return _fallback(str(e))


def _fallback(reason: str) -> dict:
    return {
        "description": "Scene analysis unavailable.",
        "energy": DEFAULT_ENERGY,
        "sentiment": DEFAULT_SENTIMENT,
        "fallback_reason": reason,
    }
