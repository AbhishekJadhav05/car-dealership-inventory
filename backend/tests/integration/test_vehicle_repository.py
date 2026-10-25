"""Integration tests for VehicleRepository against a real Postgres database."""

from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.vehicles.models import Category, Vehicle
from app.vehicles.repository import VehicleRepository


@pytest.fixture()
def repo(db_session: Session) -> VehicleRepository:
    return VehicleRepository(db_session)


def _create(
    repo: VehicleRepository,
    make: str = "Toyota",
    model: str = "Camry",
    category: Category = Category.sedan,
    price: Decimal = Decimal("25000.00"),
    quantity: int = 5,
) -> Vehicle:
    """Typed helper so tests don't have to repeat boilerplate kwargs."""
    return repo.create(make=make, model=model, category=category, price=price, quantity=quantity)


def test_create_persists_vehicle_and_returns_id(repo: VehicleRepository) -> None:
    vehicle = _create(repo)

    assert vehicle.id is not None
    assert vehicle.make == "Toyota"


def test_get_by_id_finds_existing_vehicle(repo: VehicleRepository) -> None:
    vehicle = _create(repo)

    found = repo.get_by_id(vehicle.id)

    assert found is not None
    assert found.id == vehicle.id


def test_get_by_id_returns_none_for_unknown(repo: VehicleRepository) -> None:
    assert repo.get_by_id(99999) is None


def test_list_all_returns_all_vehicles(repo: VehicleRepository) -> None:
    _create(repo, make="Toyota")
    _create(repo, make="Honda")

    assert len(repo.list_all()) == 2


def test_atomic_purchase_decreases_quantity(repo: VehicleRepository) -> None:
    vehicle = _create(repo, quantity=5)

    result = repo.atomic_purchase(vehicle.id, quantity=2)

    assert result is not None
    assert result.quantity == 3


def test_atomic_purchase_returns_none_when_out_of_stock(repo: VehicleRepository) -> None:
    vehicle = _create(repo, quantity=1)

    result = repo.atomic_purchase(vehicle.id, quantity=5)

    assert result is None
