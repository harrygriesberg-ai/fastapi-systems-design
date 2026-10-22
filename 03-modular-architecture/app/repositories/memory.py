from app.domain.models import Product
from app.repositories.base import ProductRepository


class InMemoryProductRepository(ProductRepository):
    def __init__(self) -> None:
        self._items: dict[int, Product] = {}
        self._next_id = 1

    def list(self) -> list[Product]:
        return list(self._items.values())

    def get(self, product_id: int) -> Product | None:
        return self._items.get(product_id)

    def add(self, name: str, price: float) -> Product:
        product = Product(id=self._next_id, name=name, price=price)
        self._items[product.id] = product
        self._next_id += 1
        return product

    def save(self, product: Product) -> Product:
        self._items[product.id] = product
        return product
