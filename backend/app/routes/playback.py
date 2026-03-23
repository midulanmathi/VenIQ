"""
Playback State Route

GET  /api/playback/current   → what's currently queued/playing
POST /api/playback/override  → DJ manually picks a different song
"""

import random
from flask import Blueprint, request, jsonify
from app.services.deezer import fetch_chart_tracks, pick_genre_for_tags, search_deezer
from app.services.songs_db import get_song

playback_bp = Blueprint("playback", __name__)

_current: dict = {"track": None, "source": None}  # source: "auto" | "override"

# Sentiment → vibe_tags for override requests
_SENTIMENT_TAGS = {
    "party":   ["energetic", "dancing", "electronic", "euphoric", "rave"],
    "calm":    ["peaceful", "ambient", "gentle", "tranquil", "classical"],
    "focused": ["focused", "lo-fi", "study", "steady", "minimal"],
    "happy":   ["joyful", "upbeat", "feel-good", "bright", "fun"],
}


def set_current_track(track: dict, source: str = "auto") -> None:
    """Called by the crowd route when a new track is auto-selected."""
    _current["track"] = track
    _current["source"] = source


@playback_bp.route("/current", methods=["GET"])
def current():
    return jsonify(_current)


@playback_bp.route("/override", methods=["POST"])
def override():
    """
    Body (JSON), one of:
        { "track": { "name": "...", "artist": "...", ... } }
        { "sentiment": "party" }  → pick a fresh song for that sentiment
    """
    data = request.get_json(silent=True) or {}

    if "track" in data:
        track = data["track"]

    elif "sentiment" in data:
        sentiment = data["sentiment"]
        vibe_tags = _SENTIMENT_TAGS.get(sentiment, ["upbeat", "feel-good"])

        # Try Deezer charts first
        genre_id = pick_genre_for_tags(vibe_tags)
        chart_tracks = fetch_chart_tracks(genre_id, limit=100)
        if not chart_tracks:
            chart_tracks = fetch_chart_tracks(0, limit=100)

        if chart_tracks:
            chosen = random.choice(chart_tracks[:30])
            track = {
                "name":        chosen["title"],
                "artist":      chosen["artist"]["name"],
                "preview_url": chosen["preview"],
                "cover_url":   chosen["album"].get("cover_medium", ""),
                "deezer_url":  chosen.get("link", ""),
                "deezer_id":   chosen["id"],
                "bpm":         None,
                "key":         None,
                "genre":       None,
                "duration_s":  chosen.get("duration"),
            }
        else:
            # Static DB fallback
            energy = {"party": 8, "happy": 7, "focused": 5, "calm": 3}.get(sentiment, 5)
            song = get_song(sentiment, energy)
            if not song:
                return jsonify({"error": "No tracks found for that sentiment"}), 404
            dz = search_deezer(song["name"], song["artist"])
            track = {
                "name":        song["name"],
                "artist":      song["artist"],
                "bpm":         song["bpm"],
                "key":         song["key"],
                "genre":       song["genre"],
                "duration_s":  song["duration_s"],
                "preview_url": dz["preview_url"] if dz else None,
                "deezer_url":  dz["deezer_url"]  if dz else None,
                "deezer_id":   dz["deezer_id"]   if dz else None,
                "cover_url":   dz["cover_url"]   if dz else None,
            }
    else:
        return jsonify({"error": "Provide 'track' or 'sentiment'"}), 400

    set_current_track(track, source="override")
    return jsonify({"track": track, "source": "override"})
