import jwt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories.users import UserRepository
from app.schemas.auth import RegisterRequest, TokenPair, UserResponse
from app.security.passwords import hash_password, verify_password
from app.security.tokens import (
    create_access_token,
    create_refresh_token,
    decode_token,
)


class AuthError(Exception):
    pass


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = UserRepository(db)

    def register(self, payload: RegisterRequest) -> UserResponse:
        if self.repo.by_email(payload.email):
            raise AuthError("email already registered")

        try:
            user = self.repo.add(
                payload.email,
                hash_password(payload.password),
            )
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise AuthError("email already registered") from exc

        return UserResponse(
            id=user.id,
            email=user.email,
            role=user.role,
        )

    def login(self, email: str, password: str) -> TokenPair:
        user = self.repo.by_email(email.strip().lower())

        if not user or not verify_password(password, user.password_hash):
            raise AuthError("invalid credentials")

        return self._pair(user)

    def refresh(self, token: str) -> TokenPair:
        try:
            data = decode_token(token, "refresh")
        except jwt.InvalidTokenError as exc:
            raise AuthError("invalid refresh token") from exc

        user = self.repo.by_id(int(data["sub"]))
        if not user:
            raise AuthError("user no longer exists")

        return self._pair(user)

    @staticmethod
    def _pair(user) -> TokenPair:
        subject = str(user.id)
        return TokenPair(
            access_token=create_access_token(subject, user.role),
            refresh_token=create_refresh_token(subject, user.role),
        )
