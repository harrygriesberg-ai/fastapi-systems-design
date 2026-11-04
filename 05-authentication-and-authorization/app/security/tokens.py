from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import get_settings


def _encode(
    subject: str,
    role: str,
    token_type: str,
    expires: timedelta,
) -> str:
    now = datetime.now(timezone.utc)
    settings = get_settings()
    payload = {
        "sub": subject,
        "role": role,
        "typ": token_type,
        "iat": now,
        "exp": now + expires,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def create_access_token(subject: str, role: str) -> str:
    return _encode(
        subject,
        role,
        "access",
        timedelta(minutes=get_settings().access_token_minutes),
    )


def create_refresh_token(subject: str, role: str) -> str:
    return _encode(
        subject,
        role,
        "refresh",
        timedelta(days=get_settings().refresh_token_days),
    )


def decode_token(token: str, expected_type: str) -> dict:
    data = jwt.decode(
        token,
        get_settings().jwt_secret,
        algorithms=["HS256"],
    )
    if data.get("typ") != expected_type:
        raise jwt.InvalidTokenError("wrong token type")
    return data
