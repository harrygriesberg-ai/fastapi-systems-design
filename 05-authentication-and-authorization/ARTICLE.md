# Authentication in FastAPI — Password Hashing, JWTs, and Authorization

Authentication code is easy to demo and easy to get dangerously wrong.

A login endpoint that returns a JWT can fit on one screen, but a secure identity flow is a collection of decisions:

- how passwords are stored;
- how tokens are signed and expired;
- how callers are loaded;
- how permissions are checked;
- how refresh tokens are handled;
- how sessions are revoked after compromise.

This lesson implements a compact authentication flow while being explicit about what the teaching project does **not** provide.

```text
Register
  │
  ├── validate email/password
  ├── hash password
  └── store user

Login
  │
  ├── load user
  ├── verify password hash
  └── issue access + refresh token

Protected request
  │
  ├── verify bearer access token
  ├── load current user
  └── run authorization check
```

## Never store passwords

The database stores a password **hash**, not the original password.

The example uses Argon2:

```python
from argon2 import PasswordHasher

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _hasher.hash(password)
```

Argon2 is a password-hashing function designed to make guessing expensive.

That is different from encryption. Your application should not need to decrypt and recover the user's password.

Avoid fast general-purpose hashes such as SHA-256 for password storage. Speed is desirable for file integrity checks; it is undesirable when an attacker is trying billions of password guesses.

## Registration needs two layers of uniqueness protection

The service checks whether an email already exists before insertion.

That gives us a clean application error:

```text
email already registered
```

The database also has a unique constraint.

Why both?

Because two concurrent requests can both pass an application-level “does this exist?” check before either request inserts the row.

The database is the final authority on the invariant.

This pattern appears throughout backend systems:

```text
Application check
  → improves user-facing behavior

Database constraint
  → protects correctness under concurrency
```

## Access and refresh tokens have different jobs

An access token is short-lived and presented to normal protected endpoints.

A refresh token lives longer and exists to obtain a new access token.

The example includes a token-type claim:

```python
payload = {
    "sub": subject,
    "role": role,
    "typ": token_type,
    "iat": now,
    "exp": now + expires,
}
```

The decoder requires the expected token type:

```python
decode_token(token, "access")
```

That prevents a valid refresh token from being accepted where an access token is required.

## Use a stable subject

The `sub` claim contains the user ID.

That is usually a better internal identifier than email because users may be allowed to change email addresses.

A token should identify the account using a value whose meaning remains stable for the token's lifetime.

## JWTs are signed, not automatically private

A common misunderstanding is that JWT contents are encrypted.

A normal signed JWT is readable by the client.

Do not place passwords, secrets, private API keys, or unnecessary sensitive data in claims.

The signature protects integrity: it lets the server detect whether claims were modified.

Confidentiality still depends on transport security and what data you choose to put into the token.

## Load current account state

The authentication dependency verifies the token and then loads the current user:

```python
user = UserRepository(db).by_id(int(data["sub"]))
```

This means a deleted user is no longer accepted simply because an old JWT still has a valid signature.

It also means the application can enforce the user's **current** role.

That design requires a database lookup per protected request.

Some systems intentionally trade that freshness for more stateless verification. The correct choice depends on scale, latency, revocation requirements, and threat model.

JWT is a data format, not an architecture.

## Authentication and authorization are different

Authentication asks:

> Who is calling?

Authorization asks:

> Is this caller allowed to perform this action?

Our current-user dependency performs authentication.

A separate dependency performs admin authorization:

```python
def require_admin(user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(403, "Admin role required")

    return user
```

This separation becomes more important as permission rules grow.

A larger application might check:

- organization membership;
- resource ownership;
- OAuth scopes;
- project roles;
- subscription tier;
- explicit policy rules.

Do not bury all of that logic in a token decoder.

## 401 and 403 are not the same result

Use `401` when credentials are missing, invalid, or expired.

Use `403` when authentication succeeded but the caller does not have permission.

That distinction helps clients behave correctly:

```text
401
  → authenticate again / refresh credentials

403
  → caller is known, but action is not permitted
```

A UI can present a permissions message instead of repeatedly sending an authenticated user back to a login screen.

## The refresh-token limitation matters

The lesson issues signed refresh tokens.

It does **not** implement server-side session state.

That means a stolen refresh token may remain usable until expiration.

A production session design may include:

- refresh-token rotation;
- token identifiers;
- hashed refresh tokens in storage;
- session/device records;
- reuse detection;
- revocation after password changes;
- logout revocation;
- security-event invalidation.

A teaching example should not imply that “JWT refresh token” automatically solves session management.

## Token rotation

A stronger refresh flow commonly works like:

```text
Client sends refresh token A
        │
        ▼
Server verifies A
        │
        ├── marks A used/revoked
        └── issues refresh token B
```

If token A later appears again, the system can treat it as evidence of token theft and revoke the session family.

That requires server-side state. It is less “stateless,” but security requirements often matter more than architectural slogans.

## Algorithm handling

The decoder explicitly specifies:

```python
algorithms=["HS256"]
```

Do not accept arbitrary algorithms based only on what the incoming token says.

The sample uses a symmetric secret for simplicity.

Distributed systems may prefer asymmetric signing so one identity service holds the private key and other services verify tokens with a public key.

Key rotation and key discovery then become part of the system.

## Secrets must not live in Git

The repository contains:

```text
JWT_SECRET=change-me-in-production
```

in `.env.example` only as documentation.

A real signing secret should be:

- long and random;
- injected at runtime;
- stored in a secret manager;
- rotated according to an operational plan;
- excluded from logs.

Never copy a production secret into source control because it is “only a private repository.”

## Password policy is bigger than a regex

The example requires a minimum password length.

A real account system may also consider:

- breached-password screening;
- MFA;
- recovery flows;
- credential-stuffing protection;
- risk-based challenges;
- rate limiting;
- account lockout design.

Be cautious with complicated composition rules such as “one symbol, one uppercase character, one number.” They can encourage predictable user behavior without solving the deeper problem of password reuse and credential theft.

## Brute-force protection

The sample does not implement login rate limiting.

A public authentication endpoint should be protected against repeated guessing and credential stuffing.

Possible layers include:

```text
edge/WAF controls
per-IP limits
per-account throttling
risk scoring
MFA
anomaly detection
```

Do not create a naive account-lock policy that attackers can exploit to lock other users out.

## Browser token storage is a separate security decision

This backend accepts bearer tokens in the `Authorization` header.

A browser application still needs to decide how tokens are stored.

JavaScript-accessible storage can expose tokens to XSS.

HttpOnly cookies can reduce JavaScript access but introduce cookie/CSRF considerations.

There is no universal rule that says:

```text
JWT → localStorage
```

Design token storage and transport for the actual client environment.

## Tests should verify permission failures too

The suite tests:

- registration;
- login;
- current-user access;
- denial of an admin endpoint to a regular user.

Security tests should grow as security features grow.

Useful additional cases include:

```text
expired access token
refresh token passed as access token
invalid signature
deleted user
duplicate registration
disabled account
admin success
refresh rotation
cross-tenant authorization
```

The failure path is often more important than the success path.

## When an identity provider is the better engineering choice

Implementing authentication is valuable for learning and for systems with controlled requirements.

For many production products, an established identity provider can reduce risk and implementation work when requirements include:

- MFA;
- enterprise SSO;
- social login;
- SAML/OIDC federation;
- password recovery;
- identity verification;
- audit requirements.

Using an identity provider does not eliminate authorization work.

Your application still decides what an authenticated identity is allowed to do with your resources.

## Main lesson

Authentication is not a decorator added at the end of development.

It is a lifecycle:

```text
credential creation
credential storage
authentication
token issuance
token verification
current account state
authorization
expiration
revocation
recovery
```

Hash passwords with a dedicated password-hashing algorithm.

Keep access tokens short-lived.

Distinguish access and refresh credentials.

Validate algorithms explicitly.

Separate authentication from authorization.

And be honest about the session-management capabilities a simple JWT example does not provide.
