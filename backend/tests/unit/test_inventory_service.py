"""Unit tests for InventoryService.

All tests use InMemoryVehicleRepository — no database involved.
The fake's atomic_purchase mirrors the real SQL semantics exactly.
"""

from decimal import Decimal

import pytest

from app.core.exceptions import OutOfStock, VehicleNotFound
from app.inventory.service import InventoryService
from app.vehicles.models import Category
from tests.unit.fakes import InMemoryVehicleRepository


@pytest.fixture()
def repo() -> InMemoryVehicleRepository:
    return InMemoryVehicleRepository()


@pytest.fixture()
def service(repo: InMemoryVehicleRepository) -> InventoryService:
    return InventoryService(repo=repo)


def _seed(repo: InMemoryVehicleRepository, quantity: int = 5) -> int:
    """Create a vehicle and return its id."""
    return repo.create(
        make="Toyota",
        model="Camry",
        category=Category.sedan,
        price=Decimal("25000.00"),
        quantity=quantity,
    ).id  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# purchase
# ---------------------------------------------------------------------------


def test_purchase_decreases_quantity(
    service: InventoryService, repo: InMemoryVehicleRepository
) -> None:
    vehicle_id = _seed(repo, quantity=5)

    result = service.purchase(vehicle_id, quantity=2)

    assert result.quantity == 3


def test_purchase_raises_out_of_stock_when_quantity_is_zero(
    service: InventoryService, repo: InMemoryVehicleRepository
) -> None:
    vehicle_id = _seed(repo, quantity=0)

    with pytest.raises(OutOfStock):
        service.purchase(vehicle_id, quantity=1)


def test_purchase_raises_out_of_stock_when_insufficient(
    service: InventoryService, repo: InMemoryVehicleRepository
) -> None:
    vehicle_id = _seed(repo, quantity=2)

    with pytest.raises(OutOfStock):
        service.purchase(vehicle_id, quantity=5)


# ---------------------------------------------------------------------------
# restock
# ---------------------------------------------------------------------------


def test_restock_increases_quantity(
    service: InventoryService, repo: InMemoryVehicleRepository
) -> None:
    vehicle_id = _seed(repo, quantity=2)

    result = service.restock(vehicle_id, quantity=10)

    assert result.quantity == 12


def test_restock_raises_vehicle_not_found(service: InventoryService) -> None:
    with pytest.raises(VehicleNotFound):
        service.restock(999, quantity=5)
