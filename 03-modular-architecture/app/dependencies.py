from functools import lru_cache

from app.repositories.memory import InMemoryProductRepository
from app.services.product_service import ProductService


@lru_cache
def get_repository() -> InMemoryProductRepository:
    return InMemoryProductRepository()


def get_product_service() -> ProductService:
    return ProductService(get_repository())
