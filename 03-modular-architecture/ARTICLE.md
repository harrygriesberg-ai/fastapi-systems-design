# How I Structure FastAPI Applications That Need to Grow

Architecture discussions become abstract quickly. One side argues that every application needs layers, repositories, domain models, and dependency inversion. The other side points out that a 200-line service does not need the structure of a bank.

Both observations are correct.

The useful question is not:

> Which architecture is universally best?

It is:

> Where should I create a boundary so that likely changes stay local?

This lesson builds a product catalog around four concepts: an HTTP adapter, a service, a domain model, and a repository interface.

```text
HTTP request
    │
    ▼
FastAPI router
    │
    ▼
ProductService
    │
    ▼
ProductRepository
    │
    ▼
In-memory implementation
```

The amount of code is still small. The difference is that dependencies point toward behavior rather than toward a specific transport or storage technology.

## Route layer: translate HTTP, do not own the application

The route receives validated data, obtains a service, calls one application operation, and maps expected failures into HTTP responses.

```python
@router.post("", response_model=ProductResponse, status_code=201)
def create_product(
    payload: ProductCreate,
    service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    return service.create(payload)
```

The route does not know how products are stored.

That is not merely a style preference. It makes the behavior reusable outside HTTP and reduces the number of concerns each test must initialize.

## Service layer: express use cases

A service should represent things the application can do.

In this lesson those operations are:

```text
create product
list active products
deactivate product
```

The deactivation use case looks like this:

```python
class ProductService:
    def __init__(self, repository: ProductRepository) -> None:
        self.repository = repository

    def deactivate(self, product_id: int) -> ProductResponse:
        product = self.repository.get(product_id)

        if product is None:
            raise ProductNotFoundError(product_id)

        product.active = False
        return self._out(self.repository.save(product))
```

Notice what is missing:

- no `Depends`;
- no `HTTPException`;
- no URL path;
- no SQLAlchemy;
- no database configuration.

The service is plain Python.

If deactivation later requires checking open orders, recording an audit event, or publishing a message, that behavior has a natural home.

## Domain model: represent internal state deliberately

The project defines a simple dataclass:

```python
@dataclass(slots=True)
class Product:
    id: int
    name: str
    price: float
    active: bool = True
```

Why introduce this when Pydantic could represent the same fields?

Because the public API contract and internal application state evolve for different reasons.

A Pydantic response may later exclude internal state. A SQLAlchemy model may include persistence-only fields. A domain object may gain behavior that has no reason to appear in either representation.

You do **not** always need separate request, domain, persistence, and response classes. Excessive mapping can become ceremony. Use separate representations when there is a meaningful boundary to protect.

## Repository interface: isolate persistence decisions

The service depends on an abstraction:

```python
class ProductRepository(ABC):
    @abstractmethod
    def list(self) -> list[Product]: ...

    @abstractmethod
    def get(self, product_id: int) -> Product | None: ...

    @abstractmethod
    def add(self, name: str, price: float) -> Product: ...

    @abstractmethod
    def save(self, product: Product) -> Product: ...
```

The current implementation uses a dictionary.

In Week 4, storage moves to SQLAlchemy and PostgreSQL. The point is not that most teams switch databases frequently. The value is that business behavior does not become inseparable from ORM query syntax.

## Dependency direction matters more than folder count

The important relationship is:

```text
API ─────► Service ─────► Repository contract
             │
             ▼
           Domain

Infrastructure implementation ─────► Repository contract
```

The service knows what storage capabilities it needs, but not which technology provides them.

FastAPI's dependency functions assemble the concrete object graph at the edge:

```python
@lru_cache
def get_repository() -> InMemoryProductRepository:
    return InMemoryProductRepository()


def get_product_service() -> ProductService:
    return ProductService(get_repository())
```

That is a small example of dependency inversion.

You do not need to adopt a complete “Clean Architecture” template to benefit from this idea.

## Avoid generic repositories for their own sake

A common over-engineering pattern is a giant generic repository:

```text
BaseRepository[T]
  create
  update
  delete
  find
  find_many
  count
  sort
  search
  paginate
  ...
```

Every service then becomes a thin wrapper around generic CRUD methods.

That often creates abstraction without business meaning.

A repository is more valuable when it exposes operations the application actually needs. For example:

```text
find_active_subscription_for_user()
list_expiring_contracts()
reserve_inventory()
```

Those methods communicate intent better than leaking query-building details into services.

## Test the service without FastAPI

Because `ProductService` is plain Python, its behavior can be tested directly:

```python
repository = InMemoryProductRepository()
service = ProductService(repository)

created = service.create(
    ProductCreate(name="Keyboard", price=99.0)
)

service.deactivate(created.id)

assert service.list_active() == []
```

That test is fast and precise. It proves the business behavior without testing routing, serialization, middleware, or OpenAPI.

A separate API test verifies the HTTP wiring.

This distinction matters because one giant end-to-end test suite makes failures harder to diagnose. If a pricing rule fails, you should not need to wonder whether routing or JSON serialization caused the failure.

## Architecture should reduce change cost

Layering becomes harmful when developers follow it mechanically.

Watch for warning signs:

1. Every service method simply calls one repository method.
2. Every entity has multiple identical DTO classes with no real boundary.
3. A developer must edit six files to add one simple field.
4. Repository interfaces exactly mirror ORM methods.
5. “Clean architecture” rules are enforced even when no likely source of change exists.

Architecture is supposed to reduce the cost of change.

If structure increases the cost without isolating anything meaningful, simplify it.

## The opposite failure: route functions become the whole system

At the other extreme, a route can gradually accumulate:

```text
parse request
query database
check permissions
calculate business rules
call payment API
write database
send email
format response
```

The endpoint still works, but now every concern is coupled.

Tests become large. Reuse becomes difficult. Database changes touch HTTP code. Provider failures are handled inconsistently.

A modest service boundary prevents much of that without requiring a complicated framework.

## Sync versus async is an engineering choice

This lesson uses synchronous code because its dependencies are synchronous and there is no meaningful async I/O.

FastAPI supports both `def` and `async def`.

Do not use `async` simply because FastAPI is often described as asynchronous. An `async def` route that performs blocking database or network calls can block the event loop and hurt concurrency.

Use async when:

- your I/O libraries are asynchronous;
- your workload benefits from concurrent waiting;
- your team understands the operational model;
- measurements justify the complexity.

Synchronous FastAPI with appropriate worker/thread behavior remains a valid architecture for many services.

## How this architecture evolves in Week 4

When PostgreSQL arrives, the repository implementation changes significantly:

```text
InMemoryProductRepository
        ↓ replaced by
SQLAlchemy-backed repository
```

The service concept remains.

That is how we judge whether a boundary is useful: a large infrastructure change should not force unrelated parts of the application to change.

The next lesson will also introduce a new question this in-memory example does not have: **where does the transaction begin and end?**

## What belongs in `dependencies.py`?

The dependency module is a composition layer.

Good candidates include:

- database sessions;
- repositories;
- services;
- provider clients;
- authenticated-user dependencies.

Avoid turning it into a random utility module. Its purpose is to build and provide dependencies to the web layer.

For expensive shared clients, application lifespan may be a better place to initialize resources than recreating them per request.

## Architecture diagrams should match the code

One reason many architecture documents become useless is that the diagram describes an idealized system while the code does something else.

In a teaching repository, the diagram should be directly traceable to files:

```text
Router      → app/api/routes/products.py
Service     → app/services/product_service.py
Repository  → app/repositories/
Domain      → app/domain/models.py
Schemas     → app/schemas/products.py
```

A reader should be able to move from concept to implementation immediately.

## Main lesson

Professional structure is not about maximizing folders. It is about making responsibilities obvious and changes local.

Routes know HTTP.

Services know use cases.

Repositories know persistence capabilities.

Domain models represent internal state.

Schemas define external contracts.

Dependency providers assemble the pieces.

Start with fewer boundaries when the application is tiny. Add them when they isolate a real source of change. But once business logic matters, keeping it out of HTTP handlers is one of the highest-leverage decisions you can make in a FastAPI codebase.
