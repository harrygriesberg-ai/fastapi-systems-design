from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_product_service
from app.schemas.products import ProductCreate, ProductResponse
from app.services.product_service import ProductNotFoundError, ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductResponse])
def list_products(
    service: ProductService = Depends(get_product_service),
) -> list[ProductResponse]:
    return service.list_active()


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    return service.create(payload)


@router.post("/{product_id}/deactivate", response_model=ProductResponse)
def deactivate(
    product_id: int,
    service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    try:
        return service.deactivate(product_id)
    except ProductNotFoundError as exc:
        raise HTTPException(404, "Product not found") from exc
