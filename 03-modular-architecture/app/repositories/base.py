from abc import ABC, abstractmethod

from app.domain.models import Product


class ProductRepository(ABC):
    @abstractmethod
    def list(self) -> list[Product]: ...

    @abstractmethod
    def get(self, product_id: int) -> Product | None: ...

    @abstractmethod
    def add(self, name: str, price: float) -> Product: ...

    @abstractmethod
    def save(self, product: Product) -> Product: ...
