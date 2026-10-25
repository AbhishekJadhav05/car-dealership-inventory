"""Integration tests for VehicleRepository against a real Postgres database."""

from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.vehicles.models import Category
from app.vehicles.repository import VehicleRepository

_DEFAULTS: dict[str, object] = {
    "make": "Toyota",
    "model": "Camry",
    "category": Category.sedan,
    "price": Decimal("25000.00"),
    "quantity": 5,
}


@pytest.fixture()
def repo(db_session: Session) -> VehicleRepository:
    return VehicleRepository(db_session)


def test_create_persists_vehicle_and_returns_id(repo: VehicleRepository) -> None:
    vehicle = repo.create(**_DEFAULTS)  # type: ignore[arg-type]

    assert vehicle.id is not None
    assert vehicle.make == "Toyota"


def test_get_by_id_finds_existing_vehicle(repo: VehicleRepository) -> None:
    vehicle = repo.create(**_DEFAULTS)  # type: ignore[arg-type]

    found = repo.get_by_id(vehicle.id)  # type: ignore[arg-type]

    assert found is not None
    assert found.id == vehicle.id


def test_get_by_id_returns_none_for_unknown(repo: VehicleRepository) -> None:
    assert repo.get_by_id(99999) is None


def test_list_all_returns_all_vehicles(repo: VehicleRepository) -> None:
    repo.create(**_DEFAULTS)  # type: ignore[arg-type]
    repo.create(**{**_DEFAULTS, "make": "Honda"})  # type: ignore[arg-type]

    assert len(repo.list_all()) == 2


def test_atomic_purchase_decreases_quantity(repo: VehicleRepository) -> None:
    vehicle = repo.create(**_DEFAULTS)  # type: ignore[arg-type]

    result = repo.atomic_purchase(vehicle.id, quantity=2)  # type: ignore[arg-type]

    assert result is not None
    assert result.quantity == 3


def test_atomic_purchase_returns_none_when_out_of_stock(repo: VehicleRepository) -> None:
    vehicle = repo.create(**{**_DEFAULTS, "quantity": 1})  # type: ignore[arg-type]

    result = repo.atomic_purchase(vehicle.id, quantity=5)  # type: ignore[arg-type]

    assert result is None
