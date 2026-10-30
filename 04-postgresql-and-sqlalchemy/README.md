# Week 4 — PostgreSQL and SQLAlchemy

A task API demonstrating SQLAlchemy 2.x, PostgreSQL, request-scoped sessions, service-owned transactions, Alembic migrations, filtering, and pagination.

This folder is one lesson in **FastAPI: From First API to Production**. Read `ARTICLE.md` for the
long-form explanation and use this README as the implementation and runbook reference.

## What you will learn

- Configure SQLAlchemy 2.x for PostgreSQL.
- Create request-scoped sessions with a FastAPI yield dependency.
- Separate ORM models from API schemas.
- Own commit/rollback behavior in the use-case layer.
- Manage schema evolution with Alembic.
- Test database code with dependency overrides.

## Architecture

```text
HTTP → Service/transaction → Repository → SQLAlchemy Session → PostgreSQL
```

## Repository layout

```text
.
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── tasks.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   └── task.py
│   ├── repositories/
│   │   └── tasks.py
│   ├── schemas/
│   │   └── tasks.py
│   ├── services/
│   │   └── tasks.py
│   ├── __init__.py
│   ├── dependencies.py
│   └── main.py
├── migrations/
│   ├── versions/
│   │   └── 0001_create_tasks.py
│   ├── env.py
│   └── script.py.mako
├── tests/
│   └── test_tasks.py
├── .env.example
├── alembic.ini
├── docker-compose.yml
├── Makefile
├── ARTICLE.md
├── README.md
└── pyproject.toml
```

## Requirements

- Python 3.11 or newer
- `pip`
- A virtual environment is strongly recommended

## Quick start

```bash
python -m venv .venv
# activate it
pip install -e ".[dev]"
cp .env.example .env

docker compose up -d db
alembic upgrade head
uvicorn app.main:app --reload
```

After the server starts, open:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/v1/tasks` | Create a task. |
| `GET` | `/api/v1/tasks` | Filter and paginate tasks. |
| `PATCH` | `/api/v1/tasks/{id}` | Update title or completion state. |
| `DELETE` | `/api/v1/tasks/{id}` | Delete a task. |

## Design decisions

- **Request-scoped session:** Each request owns and closes one SQLAlchemy session.
- **Service transaction boundary:** Repositories query/flush; the service commits or rolls back the use case.
- **Alembic migrations:** Schema changes are explicit deployment artifacts instead of startup side effects.
- **PostgreSQL-first development:** Docker Compose runs the same database family intended for production.

## Testing

Install development dependencies if you have not already:

```bash
pip install -e ".[dev]"
pytest
```

The test suite demonstrates:

- CRUD behavior.
- Filtering completed tasks.
- Transaction-backed updates and deletes.
- Dependency override using an isolated test database.

## Code quality

```bash
ruff check .
```

The root GitHub Actions workflow runs linting and tests for every lesson independently.

## Production notes

This project is intentionally compact enough to teach from, but it does not pretend that a demo and
a production service are identical. Before using the patterns in a production system, consider:

- Add PostgreSQL-backed CI integration tests in addition to fast SQLite tests.
- Design indexes from measured access patterns.
- Tune pool sizes against database connection limits.
- Map expected integrity errors to safe domain responses.
- Use managed secrets instead of development credentials.

## Next step

Continue with the next numbered lesson in the repository. Each lesson assumes the architectural
ideas from the previous weeks but remains runnable on its own.
