# Week 5 — Authentication and Authorization

A compact authentication service with Argon2 password hashing, JWT access/refresh tokens, current-user dependencies, and role-based authorization.

This folder is one lesson in **FastAPI: From First API to Production**. Read `ARTICLE.md` for the
long-form explanation and use this README as the implementation and runbook reference.

## What you will learn

- Hash and verify passwords with Argon2.
- Issue and validate typed JWT access and refresh tokens.
- Build an authenticated-current-user dependency.
- Separate authentication from authorization.
- Protect role-restricted endpoints.
- Understand the revocation limitations of a stateless refresh-token demo.

## Architecture

```text
Credentials → AuthService → password/JWT security → user repository → protected dependencies
```

## Repository layout

```text
.
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py
│   │       └── users.py
│   ├── core/
│   │   └── config.py
│   ├── models/
│   │   └── user.py
│   ├── repositories/
│   │   └── users.py
│   ├── schemas/
│   │   └── auth.py
│   ├── security/
│   │   ├── passwords.py
│   │   └── tokens.py
│   ├── services/
│   │   └── auth.py
│   ├── __init__.py
│   ├── db.py
│   ├── dependencies.py
│   └── main.py
├── scripts/
│   └── create_tables.py
├── tests/
│   └── test_auth.py
├── .env.example
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
python scripts/create_tables.py
uvicorn app.main:app --reload
```

Before any real deployment, replace `JWT_SECRET` with a strong secret delivered through a secret-management system.

After the server starts, open:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/v1/auth/register` | Create an account and hash its password. |
| `POST` | `/api/v1/auth/login` | Verify credentials and issue access/refresh tokens. |
| `POST` | `/api/v1/auth/refresh` | Exchange a refresh token for a new pair. |
| `GET` | `/api/v1/users/me` | Return the authenticated user. |
| `GET` | `/api/v1/users` | Admin-only user listing. |

## Design decisions

- **Argon2:** Passwords are stored as password hashes, never plaintext.
- **Typed JWTs:** A `typ` claim prevents refresh tokens from being accepted as access tokens.
- **Current-state lookup:** Protected requests load the current user rather than relying only on stale claims.
- **Separate authorization:** Admin permission is a distinct check after authentication.

## Testing

Install development dependencies if you have not already:

```bash
pip install -e ".[dev]"
pytest
```

The test suite demonstrates:

- Registration and login.
- Bearer-token access to `/users/me`.
- 403 response when a normal user calls an admin endpoint.

## Code quality

```bash
ruff check .
```

The root GitHub Actions workflow runs linting and tests for every lesson independently.

## Production notes

This project is intentionally compact enough to teach from, but it does not pretend that a demo and
a production service are identical. Before using the patterns in a production system, consider:

- Add refresh-token rotation and revocation storage.
- Add rate limiting and abuse protection to credential endpoints.
- Use HTTPS and design browser token storage deliberately.
- Use a managed identity provider when SSO/MFA/federation requirements justify it.
- Replace the teaching `create_tables.py` approach with migrations for production.

## Next step

Continue with the next numbered lesson in the repository. Each lesson assumes the architectural
ideas from the previous weeks but remains runnable on its own.
