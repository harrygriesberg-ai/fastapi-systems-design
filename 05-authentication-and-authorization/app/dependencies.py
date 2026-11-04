from collections.abc import Generator

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.repositories.users import UserRepository
from app.security.tokens import decode_token

security = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
):
    if credentials is None:
        raise HTTPException(401, "Missing bearer token")

    try:
        data = decode_token(credentials.credentials, "access")
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            401,
            "Invalid or expired access token",
        ) from exc

    user = UserRepository(db).by_id(int(data["sub"]))
    if not user:
        raise HTTPException(401, "User no longer exists")

    return user


def require_admin(user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(403, "Admin role required")
    return user
