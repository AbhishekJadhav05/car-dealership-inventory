"""VehicleService: business logic for vehicle CRUD and search."""

from decimal import Decimal

from app.core.exceptions import VehicleNotFound
from app.vehicles.models import Category, Vehicle
from app.vehicles.repository import VehicleRepositoryProtocol


class VehicleService:
    """Facade over VehicleRepository for all vehicle operations."""

    def __init__(self, repo: VehicleRepositoryProtocol) -> None:
        self._repo = repo

    def create(
        self,
        make: str,
        model: str,
        category: Category,
        price: Decimal,
        quantity: int,
    ) -> Vehicle:
        return self._repo.create(
            make=make, model=model, category=category, price=price, quantity=quantity
        )

    def list_all(self) -> list[Vehicle]:
        """Return all vehicles including those with zero stock."""
        return self._repo.list_all()

    def search(
        self,
        *,
        make: str | None = None,
        model: str | None = None,
        category: Category | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
    ) -> list[Vehicle]:
        return self._repo.search(
            make=make,
            model=model,
            category=category,
            min_price=min_price,
            max_price=max_price,
        )

    def get(self, vehicle_id: int) -> Vehicle:
        vehicle = self._repo.get_by_id(vehicle_id)
        if vehicle is None:
            raise VehicleNotFound(vehicle_id)
        return vehicle

    def update(self, vehicle_id: int, **fields: object) -> Vehicle:
        vehicle = self._repo.update(vehicle_id, **fields)
        if vehicle is None:
            raise VehicleNotFound(vehicle_id)
        return vehicle

    def delete(self, vehicle_id: int) -> None:
        if not self._repo.delete(vehicle_id):
            raise VehicleNotFound(vehicle_id)
