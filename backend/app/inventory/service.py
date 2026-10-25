"""InventoryService: purchase and restock operations."""

from app.core.exceptions import OutOfStock, VehicleNotFound
from app.vehicles.models import Vehicle
from app.vehicles.repository import VehicleRepositoryProtocol


class InventoryService:
    """Handles stock mutations.

    Uses the same VehicleRepositoryProtocol as VehicleService so the same
    fake can be injected in unit tests without any extra wiring.
    """

    def __init__(self, repo: VehicleRepositoryProtocol) -> None:
        self._repo = repo

    def purchase(self, vehicle_id: int, quantity: int) -> Vehicle:
        """Decrease stock atomically.

        Raises VehicleNotFound if the vehicle does not exist.
        Raises OutOfStock if stock is insufficient.
        """
        result = self._repo.atomic_purchase(vehicle_id, quantity)
        if result is None:
            # atomic_purchase returns None for both "not found" and "out of stock".
            # A follow-up lookup disambiguates so the API returns the right status.
            if self._repo.get_by_id(vehicle_id) is None:
                raise VehicleNotFound(vehicle_id)
            raise OutOfStock(vehicle_id)
        return result

    def restock(self, vehicle_id: int, quantity: int) -> Vehicle:
        """Increase stock.

        Raises VehicleNotFound if the vehicle does not exist.
        """
        result = self._repo.restock(vehicle_id, quantity)
        if result is None:
            raise VehicleNotFound(vehicle_id)
        return result
