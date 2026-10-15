from app.core.errors import DomainError
from app.schemas.orders import OrderCreate, OrderResponse


class OrderService:
    VALID_COUPONS = {"SAVE10": 0.10, "SAVE20": 0.20}

    def __init__(self) -> None:
        self._orders: dict[int, OrderResponse] = {}
        self._next_id = 1

    def create(self, payload: OrderCreate) -> OrderResponse:
        subtotal = round(sum(i.quantity * i.unit_price for i in payload.items), 2)
        discount_rate = 0.0

        if payload.coupon_code:
            if payload.coupon_code not in self.VALID_COUPONS:
                raise DomainError(
                    "invalid_coupon",
                    "The supplied coupon code is not valid.",
                )
            discount_rate = self.VALID_COUPONS[payload.coupon_code]

        discount = round(subtotal * discount_rate, 2)
        result = OrderResponse(
            id=self._next_id,
            customer_id=payload.customer_id,
            currency=payload.currency,
            subtotal=subtotal,
            discount=discount,
            total=round(subtotal - discount, 2),
            item_count=sum(i.quantity for i in payload.items),
        )
        self._orders[result.id] = result
        self._next_id += 1
        return result

    def get(self, order_id: int) -> OrderResponse:
        try:
            return self._orders[order_id]
        except KeyError as exc:
            raise DomainError("order_not_found", "Order was not found.", 404) from exc
