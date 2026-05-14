from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.api.routes import health as health_module
from app.main import app

client = TestClient(app)


def test_health_db_ok_cf_loaded():
    mock_conn = MagicMock()
    mock_conn.execute.return_value = None
    mock_conn.__enter__ = lambda s: s
    mock_conn.__exit__ = MagicMock(return_value=False)

    with (
        patch("app.api.routes.health.engine") as mock_engine,
        patch("app.api.routes.health.cf_model") as mock_cf,
    ):
        mock_engine.connect.return_value = mock_conn
        mock_cf.available = True
        response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["db"] == "ok"
    assert data["cf_model"] == "loaded"


def test_health_db_ok_cf_unavailable():
    mock_conn = MagicMock()
    mock_conn.execute.return_value = None
    mock_conn.__enter__ = lambda s: s
    mock_conn.__exit__ = MagicMock(return_value=False)

    with (
        patch("app.api.routes.health.engine") as mock_engine,
        patch("app.api.routes.health.cf_model") as mock_cf,
    ):
        mock_engine.connect.return_value = mock_conn
        mock_cf.available = False
        response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["db"] == "ok"
    assert data["cf_model"] == "unavailable"


def test_health_db_error_returns_503():
    with (
        patch("app.api.routes.health.engine") as mock_engine,
        patch("app.api.routes.health.cf_model") as mock_cf,
    ):
        mock_engine.connect.side_effect = Exception("connection refused")
        mock_cf.available = False
        response = client.get("/health")

    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "error"
    assert "connection refused" in data["db"]
    assert data["cf_model"] == "unavailable"