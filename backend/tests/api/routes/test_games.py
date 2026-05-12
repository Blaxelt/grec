from unittest.mock import MagicMock
from fastapi.testclient import TestClient

import app.api.deps as deps
from app.main import app
from app.models import Game, GameTagResult

client = TestClient(app)

def make_game(**kwargs) -> Game:
    """Build a Game instance for use in tests."""
    defaults = dict(
        app_id=1,
        game_name="Test Game",
        header_image="https://example.com/img.jpg",
        short_description="A great game.",
        genres=["Action", "RPG"],
        tags=["Singleplayer", "Open World"],
        screenshots=["https://example.com/ss1.jpg"],
        combined_vector=[0.0] * 867,
        wilson_score=0.85,
    )
    defaults.update(kwargs)
    return Game(**defaults)


def mock_session(rows=None, game=None, total=None):
    """Return a MagicMock session pre-configured for the given scenario."""
    session = MagicMock()
    session.get.return_value = game
    if total is not None:
        count_result = MagicMock()
        count_result.one.return_value = total
        data_result = MagicMock()
        data_result.all.return_value = rows or []
        session.exec.side_effect = [count_result, data_result]
    else:
        session.exec.return_value.all.return_value = rows or []
    return session


# ---------------------------------------------------------------------------
# GET /games/search
# ---------------------------------------------------------------------------

def test_search_returns_matching_games():
    app.dependency_overrides[deps.get_session] = lambda: mock_session(rows=[(1, "Dark souls 1"), (2, "Dark souls 2")])
    response = client.get("/games/search?q=Dark souls")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["game_name"] == "Dark souls 1"
    assert data[1]["game_name"] == "Dark souls 2"


def test_search_returns_empty_list_when_no_match():
    app.dependency_overrides[deps.get_session] = lambda: mock_session(rows=[])
    response = client.get("/games/search?q=Fallout 5")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == []


def test_search_rejects_empty_query():
    response = client.get("/games/search?q=")
    assert response.status_code == 422


def test_search_missing_query_param_returns_422():
    response = client.get("/games/search")
    assert response.status_code == 422


def test_search_limit_above_max_returns_422():
    response = client.get("/games/search?q=A&limit=999")
    assert response.status_code == 422


def test_search_limit_below_min_returns_422():
    response = client.get("/games/search?q=A&limit=0")
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /games/{app_id}
# ---------------------------------------------------------------------------

def test_get_game_returns_detail():
    game = make_game(app_id=42, game_name="Space Explorer")
    app.dependency_overrides[deps.get_session] = lambda: mock_session(game=game)
    response = client.get("/games/42")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["app_id"] == 42
    assert data["game_name"] == "Space Explorer"
    assert data["genres"] == ["Action", "RPG"]
    assert data["tags"] == ["Singleplayer", "Open World"]
    assert "wilson_score" in data
    assert "screenshots" in data


def test_get_game_returns_404_when_not_found():
    app.dependency_overrides[deps.get_session] = lambda: mock_session(game=None)
    response = client.get("/games/99999")
    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Game not found"


def test_get_game_non_integer_id_returns_422():
    response = client.get("/games/not-an-id")
    assert response.status_code == 422


def test_get_game_header_image_fallback_to_empty_string():
    game = make_game(app_id=7, header_image=None)
    app.dependency_overrides[deps.get_session] = lambda: mock_session(game=game)
    response = client.get("/games/7")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["header_image"] == ""


def test_get_game_screenshots_fallback_to_empty_list():
    game = make_game(app_id=8, screenshots=None)
    app.dependency_overrides[deps.get_session] = lambda: mock_session(game=game)
    response = client.get("/games/8")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["screenshots"] == []

# ---------------------------------------------------------------------------
# GET /games/tags
# ---------------------------------------------------------------------------

def test_get_tags_returns_tags():
    app.dependency_overrides[deps.get_session] = lambda: mock_session(rows=["Action", "Action RPG"])
    response = client.get("/games/tags?q=Action&limit=2")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert "Action" in data
    assert "Action RPG" in data

def test_get_tags_returns_empty_list_when_no_match():
    app.dependency_overrides[deps.get_session] = lambda: mock_session(rows=[])
    response = client.get("/games/tags?q=NonexistentTag")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == []

def test_get_tags_missing_query_param_returns_422():
    response = client.get("/games/tags")
    assert response.status_code == 422

def test_get_tags_rejects_empty_query():
    response = client.get("/games/tags?q=")
    assert response.status_code == 422

def test_get_tags_limit_above_max_returns_422():
    response = client.get("/games/tags?q=Action&limit=999")
    assert response.status_code == 422  

def test_get_tags_limit_below_min_returns_422():
    response = client.get("/games/tags?q=Action&limit=0")
    assert response.status_code == 422

# ---------------------------------------------------------------------------
# GET /games/by-tags
# ---------------------------------------------------------------------------

def test_get_by_tags_returns_games():
    app.dependency_overrides[deps.get_session] = lambda: mock_session(rows=[
        (1, "Dark Souls", "https://example.com/ds.jpg", ["Action", "RPG"]),
        (2, "Elden Ring", "https://example.com/er.jpg", ["Action", "RPG", "Open World"]),
    ], total=2)
    response = client.get("/games/by-tags?tags=Action&tags=RPG&limit=2")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["limit"] == 2
    assert data["offset"] == 0
    assert len(data["items"]) == 2
    assert data["items"][0]["app_id"] == 1
    assert data["items"][0]["game_name"] == "Dark Souls"
    assert data["items"][0]["header_image"] == "https://example.com/ds.jpg"
    assert data["items"][0]["tags"] == ["Action", "RPG"]
    assert data["items"][1]["app_id"] == 2
    assert data["items"][1]["game_name"] == "Elden Ring"
    assert data["items"][1]["header_image"] == "https://example.com/er.jpg"
    assert data["items"][1]["tags"] == ["Action", "RPG", "Open World"]


def test_get_by_tags_returns_empty_list_when_no_match():
    app.dependency_overrides[deps.get_session] = lambda: mock_session(rows=[], total=0)
    response = client.get("/games/by-tags?tags=NonexistentTag")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_get_by_tags_missing_tags_param_returns_422():
    response = client.get("/games/by-tags")
    assert response.status_code == 422


def test_get_by_tags_limit_above_max_returns_422():
    response = client.get("/games/by-tags?tags=Action&limit=101")
    assert response.status_code == 422


def test_get_by_tags_limit_below_min_returns_422():
    response = client.get("/games/by-tags?tags=Action&limit=0")
    assert response.status_code == 422


def test_get_by_tags_offset_negative_returns_422():
    response = client.get("/games/by-tags?tags=Action&offset=-1")
    assert response.status_code == 422


def test_get_by_tags_header_image_none():
    app.dependency_overrides[deps.get_session] = lambda: mock_session(rows=[
        (3, "Some Game", None, ["Action"]),
    ], total=1)
    response = client.get("/games/by-tags?tags=Action")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["items"][0]["header_image"] is None