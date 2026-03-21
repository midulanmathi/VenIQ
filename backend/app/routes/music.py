import os
import uuid
from flask import Blueprint, request, jsonify, send_file, current_app
from app.services.music_transform import transform_music

music_bp = Blueprint("music", __name__)

# In-memory session store (sufficient for hackathon scale)
_sessions: dict[str, str] = {}


@music_bp.route("/transform", methods=["POST"])
def transform():
    """
    Transform a base track according to the given mood.

    Body (JSON):
        mood (str): one of "happy" | "sad" | "anxious" | "calm"
        track_id (str, optional): filename stem in audio/base_tracks/ (default: "default")

    Returns:
        { "session_id": "<uuid>", "audio_url": "/api/music/stream/<uuid>" }
    """
    data = request.get_json(silent=True) or {}
    mood = data.get("mood", current_app.config["DEFAULT_MOOD"])
    track_id = data.get("track_id", "default")

    base_dir = current_app.config["AUDIO_BASE_TRACKS_DIR"]
    output_dir = current_app.config["AUDIO_OUTPUT_DIR"]
    fallback = current_app.config["FALLBACK_TRACK"]

    # Locate base track
    base_track = os.path.join(base_dir, f"{track_id}.mp3")
    if not os.path.exists(base_track):
        base_track = fallback

    os.makedirs(output_dir, exist_ok=True)
    session_id = str(uuid.uuid4())
    output_path = os.path.join(output_dir, f"{session_id}.mp3")

    try:
        transform_music(base_track, mood, output_path)
    except Exception:
        output_path = fallback

    _sessions[session_id] = output_path

    return jsonify({"session_id": session_id, "audio_url": f"/api/music/stream/{session_id}"})


@music_bp.route("/stream/<session_id>", methods=["GET"])
def stream(session_id: str):
    """Stream the transformed audio file for a given session."""
    path = _sessions.get(session_id)
    if not path or not os.path.exists(path):
        fallback = current_app.config["FALLBACK_TRACK"]
        if not os.path.exists(fallback):
            return jsonify({"error": "Audio not found"}), 404
        path = fallback

    return send_file(path, mimetype="audio/mpeg", conditional=True)
