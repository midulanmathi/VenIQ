"""
Playback State Route

Tracks what song is currently "playing" and allows the DJ to override it.
State is in-memory — sufficient for a single-session hackathon demo.

GET  /api/playback/current   → what's currently queued/playing
POST /api/playback/override  → DJ manually picks a different song
"""

from flask import Blueprint, request, jsonify
from app.services.spotify import get_recommendations

playback_bp = Blueprint("playback", __name__)

_current: dict = {"track": None, "source": None}  # source: "auto" | "override"


def set_current_track(track: dict, source: str = "auto") -> None:
    """Called by the crowd route when a new track is auto-selected."""
    _current["track"] = track
    _current["source"] = source


@playback_bp.route("/current", methods=["GET"])
def current():
    """
    Returns the currently queued track.

    Response:
        { "track": { name, artist, uri, preview_url, spotify_url } | null,
          "source": "auto" | "override" | null }
    """
    return jsonify(_current)


@playback_bp.route("/override", methods=["POST"])
def override():
    """
    DJ manually selects a different song.

    Body (JSON), one of:
        { "track": { "name": "...", "artist": "...", "uri": "...", ... } }
        { "sentiment": "party" }  → fetch a fresh recommendation for that sentiment

    Response:
        { "track": {...}, "source": "override" }
    """
    data = request.get_json(silent=True) or {}

    if "track" in data:
        track = data["track"]
    elif "sentiment" in data:
        tracks = get_recommendations(data["sentiment"], limit=1)
        if not tracks:
            return jsonify({"error": "No tracks found for that sentiment"}), 404
        track = tracks[0]
    else:
        return jsonify({"error": "Provide 'track' or 'sentiment'"}), 400

    set_current_track(track, source="override")
    return jsonify({"track": track, "source": "override"})
