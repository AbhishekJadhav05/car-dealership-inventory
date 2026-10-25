"""API tests for the inventory endpoints (purchase and restock)."""

from fastapi.testclient import TestClient

_VEHICLES_URL = "/api/vehicles"


def test_purchase_returns_200_and_decreases_quantity(
    client: TestClient,
    customer_headers: dict[str, str],
    created_vehicle: dict[str, object],
) -> None:
    vehicle_id = created_vehicle["id"]
    resp = client.post(
        f"{_VEHICLES_URL}/{vehicle_id}/purchase",
        json={"quantity": 2},
        headers=customer_headers,
    )

    assert resp.status_code == 200
    initial_qty = created_vehicle["quantity"]
    assert isinstance(initial_qty, int)
    assert resp.json()["quantity"] == initial_qty - 2


def test_purchase_returns_409_when_out_of_stock(
    client: TestClient,
    customer_headers: dict[str, str],
    created_vehicle: dict[str, object],
) -> None:
    vehicle_id = created_vehicle["id"]
    resp = client.post(
        f"{_VEHICLES_URL}/{vehicle_id}/purchase",
        json={"quantity": 9999},
        headers=customer_headers,
    )

    assert resp.status_code == 409


def test_restock_returns_200_for_admin(
    client: TestClient,
    admin_headers: dict[str, str],
    created_vehicle: dict[str, object],
) -> None:
    vehicle_id = created_vehicle["id"]
    resp = client.post(
        f"{_VEHICLES_URL}/{vehicle_id}/restock",
        json={"quantity": 10},
        headers=admin_headers,
    )

    assert resp.status_code == 200
    initial_qty = created_vehicle["quantity"]
    assert isinstance(initial_qty, int)
    assert resp.json()["quantity"] == initial_qty + 10


def test_restock_returns_403_for_customer(
    client: TestClient,
    customer_headers: dict[str, str],
    created_vehicle: dict[str, object],
) -> None:
    vehicle_id = created_vehicle["id"]
    resp = client.post(
        f"{_VEHICLES_URL}/{vehicle_id}/restock",
        json={"quantity": 10},
        headers=customer_headers,
    )

    assert resp.status_code == 403
