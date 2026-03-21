import os
import pytest
from unittest.mock import patch
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_transform_missing_track_falls_back(client):
    """When track_id doesn't exist and no fallback, still returns a response."""
    res = client.post("/api/music/transform", json={"mood": "calm", "track_id": "nonexistent"})
    # Should not 500 — falls back to fallback track or returns error gracefully
    assert res.status_code in {200, 404}


def test_transform_valid_moods_accepted(client):
    for mood in ["happy", "sad", "anxious", "calm"]:
        res = client.post("/api/music/transform", json={"mood": mood})
        assert res.status_code in {200, 404}  # 404 only if no audio files present


def test_stream_unknown_session_returns_404_or_fallback(client):
    res = client.get("/api/music/stream/fake-session-id")
    assert res.status_code in {200, 404}
