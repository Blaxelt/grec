from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.models import GameRecommendation
from app.core.db import get_session

client = TestClient(app)

FAKE_RECOMMENDATIONS = [
    GameRecommendation(app_id=1, game_name="Dark Souls 1", header_image="https://example.com/img1.jpg", hybrid_score=0.72),
    GameRecommendation(app_id=2, game_name="Dark Souls 2", header_image="https://example.com/img2.jpg", hybrid_score=0.56),
]

MOCK_TARGET = "Elden Ring"


# ---------------------------------------------------------------------------
# GET /recommend
# ---------------------------------------------------------------------------

def test_recommendations_returns_similar_games():
    with patch("app.api.routes.recommendations.recommender.find_similar_games") as mock_find:
        mock_find.return_value = (MOCK_TARGET, FAKE_RECOMMENDATIONS)
        response = client.get("/recommend?game=Elden Ring")

    assert response.status_code == 200
    data = response.json()
    assert data["target_game"] == MOCK_TARGET
    assert len(data["recommendations"]) == 2
    assert data["recommendations"][0]["game_name"] == "Dark Souls 1"
    assert data["recommendations"][1]["game_name"] == "Dark Souls 2"


def test_recommendations_returns_404_when_game_not_found():
    with patch("app.api.routes.recommendations.recommender.find_similar_games") as mock_find:
        mock_find.return_value = None
        response = client.get("/recommend?game=Fallout 5")

    assert response.status_code == 404
    assert response.json()["detail"] == "Game 'Fallout 5' not found"


def test_recommendations_returns_422_when_game_is_empty():
    response = client.get("/recommend?game=")
    assert response.status_code == 422


def test_recommendations_returns_422_when_game_is_missing():
    response = client.get("/recommend")
    assert response.status_code == 422


def test_recommendations_returns_422_when_top_n_is_too_low():
    response = client.get("/recommend?game=Elden Ring&top_n=0")
    assert response.status_code == 422


def test_recommendations_returns_422_when_top_n_is_too_high():
    response = client.get("/recommend?game=Elden Ring&top_n=999")
    assert response.status_code == 422


def test_recommendations_returns_422_when_quality_power_is_too_low():
    response = client.get("/recommend?game=Elden Ring&quality_power=-1")
    assert response.status_code == 422


def test_recommendations_returns_422_when_quality_power_is_too_high():
    response = client.get("/recommend?game=Elden Ring&quality_power=999")
    assert response.status_code == 422

# ---------------------------------------------------------------------------
# GET /recommend/profile
# ---------------------------------------------------------------------------

FAKE_PROFILE_RECOMMENDATIONS = [
    (1, 0.72),
    (2, 0.56),
]

def make_fake_game(app_id):
    game = MagicMock()
    game.app_id = app_id
    game.game_name = f"Game {app_id}"
    game.header_image = f"http://example.com/{app_id}.jpg"
    return game

def test_get_profile_recommendations():
    fake_games = {i: make_fake_game(i) for i in [1, 2]}

    mock_session = MagicMock()
    mock_session.get.side_effect = lambda model, app_id: fake_games.get(app_id)

    app.dependency_overrides[get_session] = lambda: mock_session

    try:
        with patch("app.api.routes.recommendations.cf_model.recommend") as mock_recommend:
            mock_recommend.return_value = FAKE_PROFILE_RECOMMENDATIONS
            response = client.post("/recommend/profile", json={"app_ids": [1, 2], "hours_played": [10, 20], "top_n": 5})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert len(data["recommendations"]) == 2
    assert data["recommendations"][0]["app_id"] == 1
    assert data["recommendations"][1]["app_id"] == 2
    assert data["recommendations"][0]["hybrid_score"] == 0.72
    assert data["recommendations"][1]["hybrid_score"] == 0.56

def test_get_profile_recommendations_returns_empty_list_when_no_recommendations_found():
    with patch("app.api.routes.recommendations.cf_model.recommend") as mock_recommend:
        mock_recommend.return_value = []
        response = client.post("/recommend/profile", json={"app_ids": [1, 2], "hours_played": [10, 20], "top_n": 5})

    assert response.status_code == 200
    assert response.json()["recommendations"] == []

def test_get_profile_recommendations_returns_422_when_app_ids_is_empty():
    response = client.post("/recommend/profile", json={"app_ids": [], "hours_played": [10, 20], "top_n": 5})
    assert response.status_code == 422

def test_get_profile_recommendations_returns_422_when_hours_played_is_empty():
    response = client.post("/recommend/profile", json={"app_ids": [1, 2], "hours_played": [], "top_n": 5})
    assert response.status_code == 422

def test_get_profile_recommendations_returns_422_when_top_n_is_too_low():
    response = client.post("/recommend/profile", json={"app_ids": [1, 2], "hours_played": [10, 20], "top_n": 0})
    assert response.status_code == 422

def test_get_profile_recommendations_returns_422_when_top_n_is_too_high():
    response = client.post("/recommend/profile", json={"app_ids": [1, 2], "hours_played": [10, 20], "top_n": 999})
    assert response.status_code == 422

def test_get_profile_recommendations_returns_422_when_hours_played_is_negative():
    response = client.post("/recommend/profile", json={"app_ids": [1, 2], "hours_played": [-10, 20], "top_n": 5})
    assert response.status_code == 422

def test_get_profile_recommendations_skips_missing_db_games():
    fake_games = {1: make_fake_game(1)}

    mock_session = MagicMock()
    mock_session.get.side_effect = lambda model, app_id: fake_games.get(app_id)

    app.dependency_overrides[get_session] = lambda: mock_session

    try:
        with patch("app.api.routes.recommendations.cf_model.recommend") as mock_recommend:
            mock_recommend.return_value = FAKE_PROFILE_RECOMMENDATIONS
            response = client.post("/recommend/profile", json={"app_ids": [1, 2], "hours_played": [10, 20], "top_n": 5})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["app_id"] == 1

def test_get_profile_recommendations_returns_422_when_length_mismatch():
    response = client.post("/recommend/profile", json={"app_ids": [1, 2], "hours_played": [10], "top_n": 5})
    assert response.status_code == 422