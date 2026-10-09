# Week 1 — Building Your First Professional FastAPI API

A small CRUD service that introduces the project boundaries used throughout the series without hiding the fundamentals behind unnecessary infrastructure.

This folder is one lesson in **FastAPI: From First API to Production**. Read `ARTICLE.md` for the
long-form explanation and use this README as the implementation and runbook reference.

## What you will learn

- Create a FastAPI application factory and versioned router.
- Use Pydantic request and response schemas as explicit API contracts.
- Move application behavior into a service layer.
- Inject services with FastAPI dependencies.
- Write end-to-end API tests with `TestClient`.
- Add a health endpoint and container image.

## Architecture

```text
Client → Router → Pydantic schema → UserService → in-memory store → response schema
```

## Repository layout

```text
.
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── users.py
│   ├── core/
│   │   └── config.py
│   ├── schemas/
│   │   └── users.py
│   ├── services/
│   │   └── user_service.py
│   ├── __init__.py
│   ├── dependencies.py
│   └── main.py
├── tests/
│   └── test_api.py
├── .env.example
├── Dockerfile
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
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env  # PowerShell: Copy-Item .env.example .env
uvicorn app.main:app --reload
```

After the server starts, open:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Process health and environment. |
| `GET` | `/api/v1/users` | List users. |
| `POST` | `/api/v1/users` | Create a user. |
| `GET` | `/api/v1/users/{id}` | Read one user. |
| `PATCH` | `/api/v1/users/{id}` | Partially update a user. |
| `DELETE` | `/api/v1/users/{id}` | Delete a user. |

## Design decisions

- **Thin routes:** Routes translate HTTP into service calls instead of owning business logic.
- **Separate schemas:** Create, update, and response models have different responsibilities.
- **Cached dependency:** The in-memory service persists for one process and is easy to replace in tests.
- **Versioned API:** Public endpoints are mounted under `/api/v1` from the beginning.

## Testing

Install development dependencies if you have not already:

```bash
pip install -e ".[dev]"
pytest
```

The test suite demonstrates:

- Health behavior.
- Complete create/read/update/delete flow.
- Validation failure for malformed input.
- Not-found behavior after deletion.

## Code quality

```bash
ruff check .
```

The root GitHub Actions workflow runs linting and tests for every lesson independently.

## Production notes

This project is intentionally compact enough to teach from, but it does not pretend that a demo and
a production service are identical. Before using the patterns in a production system, consider:

- Replace in-memory state with durable storage before scaling to multiple workers.
- Add unique constraints and domain-level validation.
- Add authentication before exposing user management publicly.
- Introduce structured logging and metrics as shown in Week 7.

## Next step

Continue with the next numbered lesson in the repository. Each lesson assumes the architectural
ideas from the previous weeks but remains runnable on its own.
