from fastapi.testclient import TestClient

from app.dependencies import get_user_service
from app.main import app


def setup_function() -> None:
    get_user_service.cache_clear()


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_user_crud_flow() -> None:
    with TestClient(app) as client:
        created = client.post("/api/v1/users", json={"name": "Ada", "email": "ada@example.com"})
        assert created.status_code == 201
        user_id = created.json()["id"]

        fetched = client.get(f"/api/v1/users/{user_id}")
        assert fetched.json()["name"] == "Ada"

        updated = client.patch(f"/api/v1/users/{user_id}", json={"name": "Ada Lovelace"})
        assert updated.json()["name"] == "Ada Lovelace"

        deleted = client.delete(f"/api/v1/users/{user_id}")
        assert deleted.status_code == 204
        assert client.get(f"/api/v1/users/{user_id}").status_code == 404


def test_validation_rejects_short_name() -> None:
    with TestClient(app) as client:
        response = client.post("/api/v1/users", json={"name": "A", "email": "a@example.com"})
    assert response.status_code == 422
