from fastapi.testclient import TestClient

from app.dependencies import get_order_service
from app.main import app


def setup_function() -> None:
    get_order_service.cache_clear()


def valid_payload() -> dict:
    return {
        "customer_id": "cust-001",
        "currency": "USD",
        "items": [{"sku": "BOOK-1", "quantity": 2, "unit_price": 20.0}],
        "coupon_code": " save10 ",
    }


def test_valid_order_is_normalized_and_priced() -> None:
    with TestClient(app) as client:
        response = client.post("/api/v1/orders", json=valid_payload())

    assert response.status_code == 201
    assert response.json()["subtotal"] == 40.0
    assert response.json()["discount"] == 4.0
    assert response.json()["total"] == 36.0


def test_schema_rejects_invalid_sku() -> None:
    payload = valid_payload()
    payload["items"][0]["sku"] = "bad sku"

    with TestClient(app) as client:
        response = client.post("/api/v1/orders", json=payload)

    assert response.status_code == 422


def test_domain_error_has_stable_envelope() -> None:
    payload = valid_payload()
    payload["coupon_code"] = "NOPE"

    with TestClient(app) as client:
        response = client.post("/api/v1/orders", json=payload)

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "invalid_coupon",
            "message": "The supplied coupon code is not valid.",
        }
    }
