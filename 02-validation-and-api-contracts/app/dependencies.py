from functools import lru_cache

from app.services.order_service import OrderService


@lru_cache
def get_order_service() -> OrderService:
    return OrderService()
