# Week 3 — Modular FastAPI Architecture

A compact example of route/service/repository boundaries and dependency inversion without unnecessary enterprise ceremony.

This folder is one lesson in **FastAPI: From First API to Production**. Read `ARTICLE.md` for the
long-form explanation and use this README as the implementation and runbook reference.

## What you will learn

- Separate HTTP adapters from application use cases.
- Define a repository contract and swap infrastructure implementations.
- Use domain objects independently from HTTP schemas.
- Compose dependencies at the application edge.
- Test services without starting FastAPI.

## Architecture

```text
HTTP → Router → ProductService → ProductRepository → infrastructure implementation
```

## Repository layout

```text
.
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── products.py
│   ├── domain/
│   │   └── models.py
│   ├── repositories/
│   │   ├── base.py
│   │   └── memory.py
│   ├── schemas/
│   │   └── products.py
│   ├── services/
│   │   └── product_service.py
│   ├── __init__.py
│   ├── dependencies.py
│   └── main.py
├── tests/
│   ├── test_api.py
│   └── test_service.py
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
uvicorn app.main:app --reload
```

After the server starts, open:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/products` | List active products. |
| `POST` | `/api/v1/products` | Create a product. |
| `POST` | `/api/v1/products/{id}/deactivate` | Deactivate a product. |

## Design decisions

- **Dependency inversion:** The service depends on a repository contract rather than a concrete data store.
- **Plain Python services:** Business behavior does not import FastAPI.
- **Explicit domain model:** Internal state is separate from public request/response contracts.

## Testing

Install development dependencies if you have not already:

```bash
pip install -e ".[dev]"
pytest
```

The test suite demonstrates:

- Service behavior without HTTP.
- API wiring through `TestClient`.
- State transition from active to inactive.

## Code quality

```bash
ruff check .
```

The root GitHub Actions workflow runs linting and tests for every lesson independently.

## Production notes

This project is intentionally compact enough to teach from, but it does not pretend that a demo and
a production service are identical. Before using the patterns in a production system, consider:

- Use request-scoped repository instances when backed by a database session.
- Avoid generic repository abstractions that merely mirror an ORM.
- Add transaction boundaries around multi-step mutations.
- Introduce async only when the underlying I/O stack benefits from it.

## Next step

Continue with the next numbered lesson in the repository. Each lesson assumes the architectural
ideas from the previous weeks but remains runnable on its own.
