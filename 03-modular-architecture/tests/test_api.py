from fastapi.testclient import TestClient

from app.dependencies import get_repository
from app.main import app


def setup_function() -> None:
    get_repository.cache_clear()


def test_api_uses_same_service_boundary() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/products",
            json={"name": "Monitor", "price": 250},
        )

        assert response.status_code == 201
        assert len(client.get("/api/v1/products").json()) == 1
