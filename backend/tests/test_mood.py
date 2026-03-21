import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_mood_requires_input(client):
    res = client.post("/api/mood", json={})
    assert res.status_code == 400


def test_mood_text_returns_valid_mood(client):
    res = client.post("/api/mood", json={"text": "I feel very anxious today"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["mood"] in {"happy", "sad", "anxious", "calm"}
    assert 0.0 <= data["confidence"] <= 1.0


def test_mood_defaults_to_calm_on_neutral_text(client):
    res = client.post("/api/mood", json={"text": "blah blah nonsense xyz"})
    assert res.status_code == 200
    assert res.get_json()["mood"] == "calm"
