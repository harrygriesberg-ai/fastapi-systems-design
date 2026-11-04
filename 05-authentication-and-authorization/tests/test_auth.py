import os

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-secret-not-for-production-at-least-32-bytes"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.dependencies import get_db
from app.main import app
from app.models.user import User  # noqa: F401

engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, expire_on_commit=False)
Base.metadata.create_all(engine)


def override_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_db


def setup_function() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def test_register_login_and_me() -> None:
    with TestClient(app) as client:
        registered = client.post(
            "/api/v1/auth/register",
            json={
                "email": "User@Example.com",
                "password": "long-password-123",
            },
        )
        assert registered.status_code == 201

        login = client.post(
            "/api/v1/auth/login",
            json={
                "email": "user@example.com",
                "password": "long-password-123",
            },
        )
        assert login.status_code == 200

        token = login.json()["access_token"]
        me = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me.status_code == 200
        assert me.json()["email"] == "user@example.com"


def test_regular_user_cannot_list_users() -> None:
    with TestClient(app) as client:
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "u@example.com",
                "password": "long-password-123",
            },
        )
        token = client.post(
            "/api/v1/auth/login",
            json={
                "email": "u@example.com",
                "password": "long-password-123",
            },
        ).json()["access_token"]

        response = client.get(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403
