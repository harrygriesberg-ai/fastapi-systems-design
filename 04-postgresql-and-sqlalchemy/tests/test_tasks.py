import os

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.dependencies import get_db
from app.main import app
from app.models.task import Task  # noqa: F401

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


def test_create_list_update_delete() -> None:
    with TestClient(app) as client:
        created = client.post(
            "/api/v1/tasks",
            json={"title": "Ship article"},
        )
        assert created.status_code == 201
        task_id = created.json()["id"]

        page = client.get("/api/v1/tasks?completed=false").json()
        assert page["total"] == 1

        updated = client.patch(
            f"/api/v1/tasks/{task_id}",
            json={"completed": True},
        )
        assert updated.json()["completed"] is True

        assert client.delete(f"/api/v1/tasks/{task_id}").status_code == 204
