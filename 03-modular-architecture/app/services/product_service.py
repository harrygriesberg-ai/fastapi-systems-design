from app.repositories.base import ProductRepository
from app.schemas.products import ProductCreate, ProductResponse


class ProductNotFoundError(Exception):
    pass


class ProductService:
    def __init__(self, repository: ProductRepository) -> None:
        self.repository = repository

    def list_active(self) -> list[ProductResponse]:
        return [self._out(product) for product in self.repository.list() if product.active]

    def create(self, payload: ProductCreate) -> ProductResponse:
        product = self.repository.add(payload.name, payload.price)
        return self._out(product)

    def deactivate(self, product_id: int) -> ProductResponse:
        product = self.repository.get(product_id)
        if product is None:
            raise ProductNotFoundError(product_id)

        product.active = False
        return self._out(self.repository.save(product))

    @staticmethod
    def _out(product) -> ProductResponse:
        return ProductResponse(
            id=product.id,
            name=product.name,
            price=product.price,
            active=product.active,
        )
