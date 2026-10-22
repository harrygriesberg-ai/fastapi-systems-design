from app.repositories.memory import InMemoryProductRepository
from app.schemas.products import ProductCreate
from app.services.product_service import ProductService


def test_service_can_be_tested_without_fastapi() -> None:
    repository = InMemoryProductRepository()
    service = ProductService(repository)

    created = service.create(ProductCreate(name="Keyboard", price=99.0))
    assert created.id == 1

    service.deactivate(created.id)
    assert service.list_active() == []
