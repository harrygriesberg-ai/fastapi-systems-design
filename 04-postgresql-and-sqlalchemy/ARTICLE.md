# Building a Real FastAPI Backend with PostgreSQL and SQLAlchemy

Until this point, the series has kept state in memory so we could focus on API contracts and application boundaries. Real services need durable data, concurrency-safe constraints, migrations, transactions, and queries that remain predictable as the dataset grows.

This lesson adds PostgreSQL, SQLAlchemy 2.x, and Alembic to a task API.

```text
Client
  │
  ▼
FastAPI router
  │
  ▼
TaskService  ───── transaction boundary
  │
  ▼
TaskRepository
  │
  ▼
SQLAlchemy Session
  │
  ▼
PostgreSQL
```

The most important new concept is not “how to run a SELECT.” It is ownership of database resources and transactions.

## The SQLAlchemy model is a persistence model

SQLAlchemy's typed declarative style makes storage explicit:

```python
class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
```

This class describes how a task is stored.

The HTTP API still uses Pydantic models:

```python
class TaskCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    completed: bool
    created_at: datetime
```

The distinction is important. A database row and a public API resource often start with similar fields and diverge over time.

## One SQLAlchemy session per request

A `Session` represents a unit of work. It should not be one shared global mutable object across requests.

FastAPI's yield dependencies provide a clean lifecycle:

```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
```

Every request receives a session and that session is closed even when request handling raises an exception.

The repository and service receive the same session, so a use case can execute multiple database operations inside one transaction.

## Who owns `commit()`?

There are several valid transaction strategies, but transaction ownership should be deliberate.

In this example, the **service owns the use case**, so it commits:

```python
def create(self, payload: TaskCreate) -> TaskResponse:
    try:
        task = self.repo.add(payload.title)
        self.db.commit()
        self.db.refresh(task)
        return TaskResponse.model_validate(task)
    except Exception:
        self.db.rollback()
        raise
```

The repository is responsible for persistence operations, but it does not decide that the entire business operation is complete.

This distinction becomes critical when one service operation changes multiple records. If every repository method commits independently, an operation can be left half-finished when a later step fails.

Larger systems may use a unit-of-work abstraction or a transaction wrapper around a service call. The mechanism can vary. The important principle is that **business-operation boundaries and transaction boundaries should line up intentionally**.

## `flush`, `commit`, and `refresh`

These methods are easy to confuse.

### `flush()`

`flush()` sends pending changes to the database inside the current transaction. It does not make the transaction durable.

It is useful when you need a generated primary key before commit.

### `commit()`

`commit()` makes the transaction durable.

### `refresh()`

`refresh()` reloads the ORM object from the database.

This is useful when the database populates values such as timestamps or defaults.

Understanding those three operations prevents subtle transaction bugs and unnecessary commits.

## Repository queries should do filtering in the database

A beginner implementation may load every row and then filter in Python.

That does not scale.

The repository applies filtering, ordering, limit, and offset to SQL:

```python
query = (
    select(Task)
    .where(*filters)
    .order_by(Task.id)
    .limit(limit)
    .offset(offset)
)
```

The endpoint also caps `limit`:

```python
limit: int = Query(20, ge=1, le=100)
```

This prevents a client from accidentally requesting an unbounded result set.

## Pagination is an API design decision

Offset pagination is straightforward:

```text
limit=20
offset=40
```

It is suitable for many administration screens and modest datasets.

However, it has trade-offs:

- large offsets can become expensive;
- inserts/deletes can cause users to see duplicate or skipped rows;
- rapidly changing feeds are often better served by cursor/keyset pagination.

The right pagination strategy depends on the access pattern, not on what is easiest to demonstrate.

## `COUNT(*)` is not free

The sample returns a `total` count because it makes the example easy to use:

```json
{
  "items": [],
  "total": 184,
  "limit": 20,
  "offset": 40
}
```

But exact counts can become expensive on large filtered datasets.

Do not add an exact total to every paginated API by habit. Ask whether the UI actually needs it and measure the query cost.

## Use migrations instead of changing tables at startup

Many tutorials use:

```python
Base.metadata.create_all(engine)
```

when the app starts.

That is convenient for a disposable demo, but it is not a production schema-evolution strategy.

This lesson includes Alembic.

The development flow is:

```bash
docker compose up -d db
alembic upgrade head
uvicorn app.main:app --reload
```

A migration is a versioned deployment artifact. It can be reviewed with code and applied in a controlled order.

When SQLAlchemy models change, generate a migration and **review it**. Auto-generated migration code cannot understand every data migration or operational consequence.

## PostgreSQL in development

The project includes Docker Compose:

```yaml
services:
  db:
    image: postgres:17-alpine
```

This lets developers work against PostgreSQL instead of quietly changing the development database to SQLite.

That matters because PostgreSQL and SQLite differ in:

- types;
- concurrency;
- constraint behavior;
- locking;
- SQL functions;
- indexing;
- transaction semantics.

Using the same database family locally reduces surprises.

The credentials in the Compose file are development-only. Real deployments should inject secrets securely.

## Why the fast test suite still uses SQLite

The included test suite overrides the database dependency with an in-memory SQLite database.

That keeps normal CI:

- fast;
- isolated;
- credential-free;
- easy to run on any machine.

But this is not presented as complete PostgreSQL validation.

A mature project should add a second integration layer:

```text
Fast tests
  └── SQLite or repositories/fakes

Database integration
  └── Real PostgreSQL container/service
```

Use real PostgreSQL for behavior that depends on the dialect, concurrency, locking, extensions, or database-specific types.

## Indexes should follow real access patterns

The example includes an index on the title to demonstrate index metadata.

In production, indexes should be based on the queries the system actually executes.

Too few indexes can make important reads slow.

Too many indexes:

- consume storage;
- slow inserts and updates;
- add maintenance cost.

For important queries, inspect PostgreSQL query plans with tools such as `EXPLAIN ANALYZE` instead of relying on intuition.

## Connection pooling matters when you scale

`create_engine(..., pool_pre_ping=True)` helps identify stale connections before using them.

But production tuning involves more than that.

Consider:

```text
application instances
× worker processes
× pool size
= potential database connections
```

A backend can scale its web tier faster than PostgreSQL can accept connections.

Pool size, overflow, worker count, database limits, and a pooler such as PgBouncer may become part of the deployment design.

## Sync SQLAlchemy is still a valid FastAPI architecture

This example uses synchronous SQLAlchemy.

That is intentional.

FastAPI supports synchronous endpoints, and SQLAlchemy's sync API is mature. Async SQLAlchemy can be useful when the full stack uses async I/O and the workload benefits from concurrent waiting.

Do not convert an application to async only because “FastAPI is async.”

The correct question is whether the application's dependencies and traffic model benefit from it.

## Roll back failed writes

After a database exception, a session can remain in a failed transaction state.

That is why write methods use:

```python
try:
    ...
    self.db.commit()
except Exception:
    self.db.rollback()
    raise
```

Production code should usually catch specific expected exceptions—such as integrity violations—and map them to domain errors.

Do not return raw SQL errors to API clients.

Internal logs can contain technical context. Public responses should not expose schema names, SQL fragments, connection details, or sensitive values.

## Database constraints remain important

Pydantic validation is useful, but persistence invariants belong in the database too.

Examples include:

- unique email;
- foreign keys;
- non-null fields;
- check constraints;
- uniqueness across multiple columns.

Application checks improve error messages. Database constraints make the invariant safe under concurrency.

## Do not put every query in a service

A common misunderstanding of layered architecture is that a service should contain SQLAlchemy query syntax because “the service owns logic.”

A better separation is:

```text
Service
  └── asks for application-level data operations

Repository/data-access layer
  └── knows how to express those operations in SQLAlchemy
```

Not every project needs a repository abstraction, but once query logic becomes non-trivial, centralizing persistence behavior often improves readability and testing.

## Main lesson

Adding a database changes much more than where data is stored.

It introduces:

- resource lifetime;
- transaction ownership;
- migrations;
- consistency;
- query performance;
- connection limits;
- dialect-specific behavior.

Keep sessions request-scoped.

Let a clear application layer own transaction completion.

Keep ORM models separate from public API contracts.

Use migrations for schema evolution.

Keep fast tests fast, but validate PostgreSQL-specific behavior against PostgreSQL.

Persistence should remain an infrastructure capability—not a concern that takes over every layer of the application.
