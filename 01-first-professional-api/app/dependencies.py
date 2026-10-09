from functools import lru_cache

from app.services.user_service import UserService


@lru_cache
def get_user_service() -> UserService:
    return UserService()
