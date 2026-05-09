# backend/tests/api/routes/test_steam.py
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

FAKE_STEAM_RESPONSE = {
    "response": {
        "games": [
            {"appid": 570, "name": "Dota 2", "playtime_forever": 1200},
            {"appid": 730, "name": "CS2", "playtime_forever": 600},
            {"appid": 999, "name": "Unplayed Game", "playtime_forever": 0},
        ]
    }
}

@patch("app.api.routes.steam.STEAM_API_KEY", "fake-key")
@patch("app.api.routes.steam.requests.get")
def test_library_filters_and_sorts(mock_get):
    mock_resp = MagicMock(status_code=200)
    mock_resp.json.return_value = FAKE_STEAM_RESPONSE
    mock_get.return_value = mock_resp

    response = client.get("/steam/library/123456")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2                    
    assert data[0]["game_name"] == "Dota 2"
    assert data[0]["hours"] == 20.0
    assert data[1]["hours"] == 10.0

@patch("app.api.routes.steam.STEAM_API_KEY", None)
def test_library_returns_503_when_no_api_key():
    response = client.get("/steam/library/123456")
    assert response.status_code == 503

@patch("app.api.routes.steam.STEAM_API_KEY", "fake-key")
@patch("app.api.routes.steam.requests.get")
def test_library_returns_502_on_steam_failure(mock_get):
    mock_get.return_value = MagicMock(status_code=500)
    response = client.get("/steam/library/123456")
    assert response.status_code == 502
