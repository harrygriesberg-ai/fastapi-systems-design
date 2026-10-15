# FastAPI Validation Done Right — Pydantic, Errors, and API Contracts

Validation is often described as “making sure the client sent the right type.” That description is far too small for a production API. Validation is where an API turns an informal assumption into an explicit contract. It determines which data is accepted, how it is normalized, which combinations are legal, what the server promises to return, and how failures are communicated to clients.

In this lesson we build a small order API. The business logic is intentionally modest; the focus is the boundary around it.

## Three different kinds of rules

It helps to separate validation and policy into three categories.

**Shape rules** answer questions such as: Is `quantity` an integer? Is `items` a list? Is `currency` one of the supported values? Pydantic is an excellent place for these rules.

**Cross-field rules** depend on multiple pieces of input. For example, the total value of an order must stay below a supported limit. Pydantic model validators can enforce rules that still belong to the request contract.

**Domain rules** depend on application state or business policy. Whether a coupon currently exists is not a property of JSON syntax; it is business behavior. That belongs in a service, not a field validator.

Keeping these categories separate prevents schemas from turning into miniature service layers.

## Constrained inputs are executable documentation

The `OrderItem` model expresses useful constraints directly:

```python
class OrderItem(BaseModel):
    sku: Annotated[
        str,
        Field(min_length=3, max_length=40, pattern=r"^[A-Z0-9-]+$")
    ]
    quantity: Annotated[int, Field(ge=1, le=100)]
    unit_price: Annotated[float, Field(gt=0, le=100_000)]
```

These rules serve three audiences at once:

1. FastAPI uses them to reject invalid requests.
2. OpenAPI uses them to document the endpoint.
3. Developers can understand the contract without searching through route logic.

The same idea applies to enums. A `Currency` enum is better than a free-form string followed by an `if currency not in ...` check later in the call stack.

## Normalize at the boundary when normalization is unambiguous

Coupon codes are case-insensitive in this example. We normalize them once:

```python
@field_validator("coupon_code")
@classmethod
def normalize_coupon(cls, value: str | None) -> str | None:
    return value.strip().upper() if value else None
```

Boundary normalization is useful for whitespace, case, and other syntactic concerns where there is one obvious canonical representation.

Be careful not to silently “fix” meaningful input. If normalization can change business meaning, make that transformation explicit instead of hiding it in a validator.

## Cross-field validation

The maximum supported order value depends on all line items, so we use a model-level validator:

```python
@model_validator(mode="after")
def validate_order_total(self) -> "OrderCreate":
    total = sum(item.quantity * item.unit_price for item in self.items)

    if total > 250_000:
        raise ValueError("order total exceeds the supported limit")

    return self
```

FastAPI turns this into a request validation failure before the service executes.

This is appropriate because the rule is deterministic and depends only on the request itself. If the rule depended on customer credit, inventory, or a database record, it would belong in the service layer.

## Do not use one model for everything

A public response is a contract, not a serialization of whatever object happens to exist internally.

Our response model contains only what the API intends to publish:

```python
class OrderResponse(BaseModel):
    id: int
    customer_id: str
    currency: Currency
    subtotal: float
    discount: float
    total: float
    item_count: int
```

Later, persistence may include audit timestamps, internal risk state, provider identifiers, or operational metadata. Those fields should not appear publicly merely because someone returned an ORM model from a route.

Separate request, internal, persistence, and response representations when the boundaries matter.

## Stable errors are part of the API contract

Framework-generated validation errors are useful for malformed requests, but domain failures also need a predictable shape.

The service raises a typed error:

```python
raise DomainError(
    "invalid_coupon",
    "The supplied coupon code is not valid.",
)
```

A central exception handler maps it to:

```json
{
  "error": {
    "code": "invalid_coupon",
    "message": "The supplied coupon code is not valid."
  }
}
```

Why include a code when the message already explains the error?

Because clients should branch on a stable machine identifier, not English prose. Messages can be reworded or localized without forcing every consumer to update logic.

The same handler can map `order_not_found` to `404` while preserving the envelope. Centralization also keeps route functions from repeating the same `try/except` pattern for every business error.

## Validation is not authorization

A valid request is not necessarily an allowed request.

A schema can prove that `account_id` is a well-formed string. It cannot prove that the authenticated caller is allowed to access that account.

Likewise, validation does not replace database constraints. If a value must be globally unique, application validation can improve the user experience, but the database still needs to enforce the invariant because concurrent requests can race.

A useful separation is:

```text
Request shape and deterministic normalization → schema
Application policy and state-dependent rules  → service
Persistent invariants                         → database
Caller permissions                            → authorization
```

That split keeps each layer responsible for the rules it can enforce reliably.

## Avoid over-validating at the edge

Pydantic is powerful, which creates a temptation to place every rule in a validator.

Suppose coupon validity is stored in PostgreSQL. Querying the database from a Pydantic validator couples request parsing to infrastructure. It also makes models difficult to construct in tests and can hide I/O in places developers expect to be deterministic.

Use Pydantic aggressively for contracts, not as a replacement for the application layer.

## Test different failure classes separately

The test suite intentionally exercises both contract failures and domain failures.

An SKU such as:

```text
bad sku
```

fails the regular-expression contract and returns FastAPI's validation response.

An unknown coupon such as:

```text
NOPE
```

is syntactically valid but violates a business rule, so the API returns our stable domain error envelope.

That distinction matters because client behavior may differ. Invalid JSON or missing fields usually indicate a caller bug. A valid coupon that has expired is a normal business condition.

## Money deserves more care than this lesson gives it

The sample uses `float` to keep attention on validation and error design.

Real financial systems should usually represent money with integer minor units or `Decimal` plus explicit rounding rules. Floating-point arithmetic can introduce precision behavior that is unacceptable for billing.

This is an important habit for professional teaching material: if an example simplifies a production concern, say so clearly. A reader should be able to tell the difference between “the pattern this lesson demonstrates” and “the complete design for a financial system.”

## Contract evolution is part of API design

Once clients depend on a field, renaming or removing it is a breaking change.

Adding an optional field is normally easier on clients than changing an existing type. Making an optional field required can break integrations. Expanding an enum can also surprise consumers that assumed they knew every possible value.

OpenAPI documents the current contract, but compatibility still requires engineering judgment. For important APIs, schema-diff checks and contract tests can become part of CI.

## A note about status codes

The example returns:

- `201` when the order is created;
- `400` for an invalid business condition such as an unknown coupon;
- `404` for a missing order;
- FastAPI's validation response for an invalid request body.

Some organizations prefer `422` for selected domain validation errors. Others define a broader error taxonomy. Consistency across your API is more valuable than arguing that one status code is universally correct for every business rule.

## The main lesson

Good validation reduces ambiguity before application logic runs. Good API contracts go further: they define success and failure in forms that humans understand and machines can reliably consume.

Use Pydantic for structure, deterministic normalization, and request-local invariants. Keep stateful business policy in services, security decisions in authorization, and persistent invariants in the database.

That separation produces APIs that are strict without becoming tangled.
