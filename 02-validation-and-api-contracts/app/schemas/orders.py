from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Field, field_validator, model_validator


class Currency(StrEnum):
    USD = "USD"
    EUR = "EUR"
    AUD = "AUD"


class OrderItem(BaseModel):
    sku: Annotated[str, Field(min_length=3, max_length=40, pattern=r"^[A-Z0-9-]+$")]
    quantity: Annotated[int, Field(ge=1, le=100)]
    unit_price: Annotated[float, Field(gt=0, le=100_000)]


class OrderCreate(BaseModel):
    customer_id: Annotated[str, Field(min_length=3, max_length=50)]
    currency: Currency
    items: Annotated[list[OrderItem], Field(min_length=1, max_length=50)]
    coupon_code: str | None = Field(default=None, max_length=30)

    @field_validator("coupon_code")
    @classmethod
    def normalize_coupon(cls, value: str | None) -> str | None:
        return value.strip().upper() if value else None

    @model_validator(mode="after")
    def validate_order_total(self) -> "OrderCreate":
        total = sum(item.quantity * item.unit_price for item in self.items)
        if total > 250_000:
            raise ValueError("order total exceeds the supported limit")
        return self


class OrderResponse(BaseModel):
    id: int
    customer_id: str
    currency: Currency
    subtotal: float
    discount: float
    total: float
    item_count: int
