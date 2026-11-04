from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def add(
        self,
        email: str,
        password_hash: str,
        role: str = "user",
    ) -> User:
        user = User(
            email=email,
            password_hash=password_hash,
            role=role,
        )
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user

    def list(self) -> list[User]:
        return list(self.db.scalars(select(User).order_by(User.id)))
