from flask import Blueprint, request, jsonify, current_app
from app.services.mood_detection import get_user_mood
from app.models.schemas import MoodResponse

mood_bp = Blueprint("mood", __name__)


@mood_bp.route("", methods=["POST"])
def detect_mood():
    """
    Detect user mood from image or text input.

    Body (JSON):
        image_base64 (str): base64-encoded image from webcam
        OR
        text (str): user-provided text for sentiment analysis

    Returns:
        { "mood": "calm", "confidence": 0.87 }
    """
    data = request.get_json(silent=True) or {}

    image_b64 = data.get("image_base64")
    text = data.get("text")

    if not image_b64 and not text:
        return jsonify({"error": "Provide image_base64 or text"}), 400

    mood, confidence = get_user_mood(image_b64=image_b64, text=text)

    return jsonify(MoodResponse(mood=mood, confidence=confidence).__dict__)
