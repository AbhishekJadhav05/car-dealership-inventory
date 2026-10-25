"""API tests for the vehicles endpoints.

Covers the full HTTP contract: CRUD + admin-only delete.
All tests run in a rolled-back transaction (see tests/api/conftest.py).
"""

from fastapi.testclient import TestClient

_VEHICLES_URL = "/api/vehicles"


# ---------------------------------------------------------------------------
# POST /api/vehicles
# ---------------------------------------------------------------------------


def test_create_vehicle_returns_201(
    client: TestClient,
    customer_headers: dict[str, str],
    vehicle_payload: dict[str, object],
) -> None:
    resp = client.post(_VEHICLES_URL, json=vehicle_payload, headers=customer_headers)

    assert resp.status_code == 201
    body = resp.json()
    assert body["make"] == "Toyota"
    assert body["model"] == "Camry"
    assert body["category"] == "sedan"
    assert body["quantity"] == 5
    assert "id" in body


def test_create_vehicle_returns_401_unauthenticated(
    client: TestClient,
    vehicle_payload: dict[str, object],
) -> None:
    resp = client.post(_VEHICLES_URL, json=vehicle_payload)

    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /api/vehicles
# ---------------------------------------------------------------------------


def test_list_vehicles_returns_200(
    client: TestClient,
    customer_headers: dict[str, str],
    created_vehicle: dict[str, object],
) -> None:
    resp = client.get(_VEHICLES_URL, headers=customer_headers)

    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


def test_list_vehicles_returns_401_unauthenticated(client: TestClient) -> None:
    resp = client.get(_VEHICLES_URL)

    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /api/vehicles/search
# ---------------------------------------------------------------------------


def test_search_by_make_returns_matching_vehicles(
    client: TestClient,
    customer_headers: dict[str, str],
    created_vehicle: dict[str, object],
) -> None:
    resp = client.get(f"{_VEHICLES_URL}/search?make=Toyota", headers=customer_headers)

    assert resp.status_code == 200
    assert all(v["make"] == "Toyota" for v in resp.json())


def test_search_returns_empty_list_for_no_match(
    client: TestClient,
    customer_headers: dict[str, str],
    created_vehicle: dict[str, object],
) -> None:
    resp = client.get(f"{_VEHICLES_URL}/search?make=Nonexistent", headers=customer_headers)

    assert resp.status_code == 200
    assert resp.json() == []


# ---------------------------------------------------------------------------
# PUT /api/vehicles/:id
# ---------------------------------------------------------------------------


def test_update_vehicle_returns_200(
    client: TestClient,
    customer_headers: dict[str, str],
    created_vehicle: dict[str, object],
) -> None:
    vehicle_id = created_vehicle["id"]
    resp = client.put(
        f"{_VEHICLES_URL}/{vehicle_id}",
        json={**created_vehicle, "make": "Honda"},
        headers=customer_headers,
    )

    assert resp.status_code == 200
    assert resp.json()["make"] == "Honda"


def test_update_vehicle_returns_404_for_unknown_id(
    client: TestClient,
    customer_headers: dict[str, str],
) -> None:
    resp = client.put(
        f"{_VEHICLES_URL}/99999",
        json={
            "make": "Honda",
            "model": "Civic",
            "category": "sedan",
            "price": 20000,
            "quantity": 1,
        },
        headers=customer_headers,
    )

    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/vehicles/:id
# ---------------------------------------------------------------------------


def test_delete_vehicle_returns_204_for_admin(
    client: TestClient,
    admin_headers: dict[str, str],
    created_vehicle: dict[str, object],
) -> None:
    vehicle_id = created_vehicle["id"]
    resp = client.delete(f"{_VEHICLES_URL}/{vehicle_id}", headers=admin_headers)

    assert resp.status_code == 204


def test_delete_vehicle_returns_403_for_customer(
    client: TestClient,
    customer_headers: dict[str, str],
    created_vehicle: dict[str, object],
) -> None:
    vehicle_id = created_vehicle["id"]
    resp = client.delete(f"{_VEHICLES_URL}/{vehicle_id}", headers=customer_headers)

    assert resp.status_code == 403


def test_delete_vehicle_returns_404_for_unknown_id(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    resp = client.delete(f"{_VEHICLES_URL}/99999", headers=admin_headers)

    assert resp.status_code == 404
