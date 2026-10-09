# Building Your First Professional FastAPI API — Beyond Hello World

FastAPI has one of the best first-five-minutes experiences in backend development. A developer can install the framework, write a route, start Uvicorn, and immediately receive automatic OpenAPI documentation. That low barrier is a strength, but it can also create a false impression: because a FastAPI application *can* live in one file, many tutorials leave readers with an application that is hard to extend the moment real requirements appear.

This first lesson deliberately starts only one step beyond “Hello World.” The application is small, but it already has the boundaries we will rely on throughout the series: configuration, HTTP schemas, a service layer, dependency injection, versioned routes, tests, and a health endpoint. The goal is not to imitate a large enterprise system. The goal is to establish habits that continue to work when the codebase grows.

## What we are building

The sample API manages users in memory. Persistence is intentionally postponed until the PostgreSQL lesson so we can focus on the HTTP and application layers first.

```text
Client
  │
  ▼
FastAPI route
  │
  ▼
Pydantic request model
  │
  ▼
UserService
  │
  ▼
In-memory records
  │
  ▼
Pydantic response model
```

The important idea is the direction of responsibility. A route understands HTTP: paths, status codes, dependency injection, and serialization. The service understands application behavior. The Pydantic models define what crosses the HTTP boundary. When we later replace in-memory storage with PostgreSQL, the API contract does not need to change.

## Start with an application factory

A tiny application is often written as `app = FastAPI()` at module scope. That is perfectly valid, but wrapping creation in `create_app()` gives us a clear place for application-level configuration, routers, middleware, exception handlers, and lifecycle hooks.

```python
from fastapi import FastAPI

from app.api.routes.users import router as users_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="1.0.0")
    app.include_router(users_router, prefix="/api/v1")
    return app


app = create_app()
```

The function is not interesting because it saves lines. It is interesting because it creates a **composition root**: the place where the application is assembled.

## Configuration belongs outside business logic

Configuration values should not be scattered across route modules. We use `pydantic-settings` to load environment variables into a typed object:

```python
class Settings(BaseSettings):
    app_name: str = "FastAPI Starter API"
    app_env: str = "development"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
```

An `.env.example` documents supported settings without committing real secrets. The settings object is cached because configuration is effectively immutable during a process lifetime.

This pattern becomes more valuable later when configuration includes database URLs, JWT settings, provider keys, timeouts, and observability options.

## Treat schemas as API contracts

A common early mistake is using one model for create, update, storage, and response behavior. Those operations have different semantics, so we use separate models:

```python
class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=200)


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
```

`UserCreate` says what the client must provide to create a resource. `UserUpdate` represents a partial update. `UserResponse` describes what the server promises to publish.

This becomes especially important when persistence models later contain internal fields that should never be returned publicly.

FastAPI validates request bodies before the route is called. Invalid data returns a validation response, which means the service can focus on application behavior instead of repeatedly checking basic types and lengths.

## Keep business behavior out of route functions

It is tempting to put everything inside a decorated route:

```python
@router.post("/users")
def create_user(...):
    # validation
    # database logic
    # business rules
    # third-party calls
    # response shaping
```

That style feels efficient at the beginning and becomes expensive later. Route functions are easier to understand and test when they act as adapters between HTTP and a service:

```python
@router.post("", response_model=UserResponse, status_code=201)
def create_user(
    payload: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    return service.create_user(payload)
```

The `UserService` does not import FastAPI. That matters. We can call it from tests, a background worker, or another transport without pretending those callers are HTTP requests.

## Dependency injection without unnecessary machinery

FastAPI's dependency system is often introduced for authentication or database sessions, but it is also useful for application services:

```python
@lru_cache
def get_user_service() -> UserService:
    return UserService()
```

The route asks for a service; it does not construct one.

For this lesson, caching also preserves our in-memory data for the lifetime of one process. In a multi-process deployment this state would **not** be shared across workers, which is exactly why in-memory storage is a teaching tool rather than a production persistence strategy.

## HTTP semantics still matter

Framework convenience should not erase protocol semantics. The example uses:

- `200 OK` for successful reads and updates.
- `201 Created` when a resource is created.
- `204 No Content` when deletion succeeds and no response body is needed.
- `404 Not Found` when the resource does not exist.
- FastAPI's validation response when request data is invalid.

These choices make client behavior predictable. A frontend should not have to parse English prose to decide whether an operation succeeded.

## Version your public route surface deliberately

The router is mounted under `/api/v1`.

That does not mean you should create `/v2` casually. It simply acknowledges that public contracts evolve and gives incompatible future changes a clear boundary.

Versioning is not a substitute for compatibility discipline. Adding a new optional field is usually easier on clients than creating a new API version every few months.

## Add health checks early

A health endpoint may seem unnecessary in a beginner project:

```python
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}
```

Later, a load balancer, container orchestrator, or monitoring system needs exactly this kind of machine-readable signal.

In Week 7 we will split this idea into liveness and readiness and discuss why they should not always check the same dependencies.

## Test the behavior clients observe

FastAPI's `TestClient` lets us test the application through HTTP without running an external server:

```python
def test_user_crud_flow() -> None:
    with TestClient(app) as client:
        created = client.post(
            "/api/v1/users",
            json={"name": "Ada", "email": "ada@example.com"},
        )

        assert created.status_code == 201
```

The complete test continues through read, update, delete, and a final not-found check. Another test verifies that invalid input is rejected.

This is more useful than asserting that a private dictionary changed, because the HTTP contract is what API consumers depend on.

## Why this is still a teaching project

Professional examples should be clear about their limits. This lesson intentionally does **not** include:

- persistent storage;
- email uniqueness;
- authentication and authorization;
- centralized domain error envelopes;
- structured logging and metrics;
- multiple-worker-safe state;
- rate limiting;
- production deployment configuration.

Those are not hidden omissions. They are upcoming lessons.

A good architecture grows because requirements demand it. Starting with every possible abstraction can make a beginner project harder to understand without making it safer.

## Run it

```bash
python -m venv .venv
# activate it
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Try creating, reading, updating, and deleting users, then run:

```bash
pytest
ruff check .
```

The lesson also includes a Dockerfile so readers can see the same application packaged for a container.

## The main lesson

The difference between a demo API and a maintainable API is not the number of files. It is whether responsibilities have clear boundaries.

FastAPI should handle HTTP extremely well. Pydantic should define and validate data crossing the boundary. Services should express application behavior. Dependencies should make collaborators replaceable. Tests should verify behavior that consumers actually observe.

Those principles give us a codebase that can absorb database, security, testing, observability, and AI concerns without turning route functions into the entire architecture.
