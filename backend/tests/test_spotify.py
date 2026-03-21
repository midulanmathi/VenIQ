import pytest
from unittest.mock import patch, MagicMock
from app.services.spotify import get_recommendations, _get_access_token, _token_cache


@pytest.fixture(autouse=True)
def clear_token_cache():
    _token_cache["token"] = None
    _token_cache["expires_at"] = 0
    yield


def _mock_token_response():
    m = MagicMock()
    m.json.return_value = {"access_token": "fake_token", "expires_in": 3600}
    m.raise_for_status.return_value = None
    return m


def _mock_recommendations_response():
    m = MagicMock()
    m.json.return_value = {
        "tracks": [
            {
                "name": "Song A",
                "artists": [{"name": "Artist A"}],
                "uri": "spotify:track:111",
                "preview_url": "http://preview.example.com/a",
                "external_urls": {"spotify": "http://open.spotify.com/track/111"},
            }
        ]
    }
    m.raise_for_status.return_value = None
    return m


def test_get_recommendations_returns_tracks(monkeypatch):
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "fake_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "fake_secret")

    with patch("app.services.spotify.requests.post", return_value=_mock_token_response()), \
         patch("app.services.spotify.requests.get", return_value=_mock_recommendations_response()):
        tracks = get_recommendations("party")

    assert len(tracks) == 1
    assert tracks[0]["name"] == "Song A"
    assert tracks[0]["artist"] == "Artist A"
    assert tracks[0]["uri"] == "spotify:track:111"


def test_get_recommendations_returns_empty_on_missing_credentials(monkeypatch):
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "")
    tracks = get_recommendations("party")
    assert tracks == []


def test_token_is_cached():
    monkeypatch_env = {"SPOTIFY_CLIENT_ID": "id", "SPOTIFY_CLIENT_SECRET": "secret"}
    with patch.dict("os.environ", monkeypatch_env), \
         patch("app.services.spotify.requests.post", return_value=_mock_token_response()) as mock_post:
        _get_access_token()
        _get_access_token()  # second call should use cache
    assert mock_post.call_count == 1
