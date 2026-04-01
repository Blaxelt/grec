from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.models import GameRecommendation

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