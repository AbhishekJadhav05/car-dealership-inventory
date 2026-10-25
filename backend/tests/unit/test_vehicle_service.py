"""Unit tests for VehicleService.

All tests use InMemoryVehicleRepository — no database involved.
"""

from decimal import Decimal

import pytest

from app.core.exceptions import VehicleNotFound
from app.vehicles.models import Category
from app.vehicles.service import VehicleService
from tests.unit.fakes import InMemoryVehicleRepository

_DEFAULTS: dict[str, object] = {
    "make": "Toyota",
    "model": "Camry",
    "category": Category.sedan,
    "price": Decimal("25000.00"),
    "quantity": 5,
}


@pytest.fixture()
def repo() -> InMemoryVehicleRepository:
    return InMemoryVehicleRepository()


@pytest.fixture()
def service(repo: InMemoryVehicleRepository) -> VehicleService:
    return VehicleService(repo=repo)


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------


def test_create_returns_vehicle_with_all_fields(service: VehicleService) -> None:
    vehicle = service.create(**_DEFAULTS)  # type: ignore[arg-type]

    assert vehicle.id is not None
    assert vehicle.make == "Toyota"
    assert vehicle.model == "Camry"
    assert vehicle.category == Category.sedan
    assert vehicle.price == Decimal("25000.00")
    assert vehicle.quantity == 5


# ---------------------------------------------------------------------------
# list_all
# ---------------------------------------------------------------------------


def test_list_all_returns_every_vehicle(service: VehicleService) -> None:
    service.create(**_DEFAULTS)  # type: ignore[arg-type]
    service.create(**{**_DEFAULTS, "make": "Honda"})  # type: ignore[arg-type]

    assert len(service.list_all()) == 2


def test_list_all_includes_zero_quantity_vehicles(service: VehicleService) -> None:
    service.create(**{**_DEFAULTS, "quantity": 0})  # type: ignore[arg-type]

    assert len(service.list_all()) == 1


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------


def test_search_filters_by_make(service: VehicleService) -> None:
    service.create(**_DEFAULTS)  # type: ignore[arg-type]
    service.create(**{**_DEFAULTS, "make": "Honda"})  # type: ignore[arg-type]

    assert len(service.search(make="Toyota")) == 1
    assert len(service.search(make="Ford")) == 0


def test_search_filters_by_category(service: VehicleService) -> None:
    service.create(**_DEFAULTS)  # type: ignore[arg-type]
    service.create(**{**_DEFAULTS, "category": Category.suv})  # type: ignore[arg-type]

    results = service.search(category=Category.sedan)

    assert len(results) == 1
    assert results[0].category == Category.sedan


def test_search_filters_by_price_range(service: VehicleService) -> None:
    service.create(**{**_DEFAULTS, "price": Decimal("20000.00")})  # type: ignore[arg-type]
    service.create(**{**_DEFAULTS, "price": Decimal("30000.00")})  # type: ignore[arg-type]
    service.create(**{**_DEFAULTS, "price": Decimal("40000.00")})  # type: ignore[arg-type]

    results = service.search(min_price=Decimal("25000.00"), max_price=Decimal("35000.00"))

    assert len(results) == 1
    assert results[0].price == Decimal("30000.00")


# ---------------------------------------------------------------------------
# get / update / delete
# ---------------------------------------------------------------------------


def test_get_raises_vehicle_not_found_for_unknown_id(service: VehicleService) -> None:
    with pytest.raises(VehicleNotFound):
        service.get(999)


def test_update_returns_updated_vehicle(service: VehicleService) -> None:
    vehicle = service.create(**_DEFAULTS)  # type: ignore[arg-type]

    updated = service.update(vehicle.id, make="Honda")  # type: ignore[arg-type]

    assert updated.make == "Honda"


def test_update_raises_vehicle_not_found_for_unknown_id(service: VehicleService) -> None:
    with pytest.raises(VehicleNotFound):
        service.update(999, make="Honda")  # type: ignore[arg-type]


def test_delete_raises_vehicle_not_found_for_unknown_id(service: VehicleService) -> None:
    with pytest.raises(VehicleNotFound):
        service.delete(999)
