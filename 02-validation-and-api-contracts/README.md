# Week 2 — Validation and API Contracts

An order API focused on strict Pydantic contracts, normalization, cross-field validation, domain errors, and predictable failure responses.

This folder is one lesson in **FastAPI: From First API to Production**. Read `ARTICLE.md` for the
long-form explanation and use this README as the implementation and runbook reference.

## What you will learn

- Use constrained fields, enums, field validators, and model validators.
- Separate syntactic validation from domain policy.
- Design explicit response models.
- Return stable machine-readable domain error codes.
- Test schema failures separately from business-rule failures.

## Architecture

```text
Client → Pydantic contract → Route → OrderService → domain result/error → response envelope
```

## Repository layout

```text
.
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── orders.py
│   ├── core/
│   │   └── errors.py
│   ├── schemas/
│   │   └── orders.py
│   ├── services/
│   │   └── order_service.py
│   ├── __init__.py
│   ├── dependencies.py
│   └── main.py
├── tests/
│   └── test_orders.py
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
| `POST` | `/api/v1/orders` | Validate, price, and create an order. |
| `GET` | `/api/v1/orders/{id}` | Read a created order. |

## Design decisions

- **Schema rules:** Shape, ranges, formats, and deterministic normalization are enforced before service execution.
- **Domain errors:** State/policy failures use a stable error code and centralized exception handler.
- **Separate responses:** The public response is intentionally different from the incoming request.

## Testing

Install development dependencies if you have not already:

```bash
pip install -e ".[dev]"
pytest
```

The test suite demonstrates:

- Valid order pricing and normalization.
- Pydantic rejection of an invalid SKU.
- Stable domain-error envelope for an unknown coupon.

## Code quality

```bash
ruff check .
```

The root GitHub Actions workflow runs linting and tests for every lesson independently.

## Production notes

This project is intentionally compact enough to teach from, but it does not pretend that a demo and
a production service are identical. Before using the patterns in a production system, consider:

- Use `Decimal` or integer minor units for real money.
- Add request IDs and structured logging for error correlation.
- Document compatibility rules for public API changes.
- Keep authorization separate from validation.

## Next step

Continue with the next numbered lesson in the repository. Each lesson assumes the architectural
ideas from the previous weeks but remains runnable on its own.
