"""Inventory router: purchase and restock endpoints.

Both endpoints commit explicitly before returning so the data is durable
before the response is sent.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.deps import AdminUser, CurrentUser, DbSession
from app.inventory.service import InventoryService
from app.vehicles.repository import VehicleRepository
from app.vehicles.schemas import QuantityRequest, VehicleResponse

router = APIRouter(prefix="/api/vehicles", tags=["inventory"])


def _build_service(session: DbSession) -> InventoryService:
    return InventoryService(repo=VehicleRepository(session))


InventoryServiceDep = Annotated[InventoryService, Depends(_build_service)]


@router.post("/{vehicle_id}/purchase", response_model=VehicleResponse)
def purchase(
    vehicle_id: int,
    body: QuantityRequest,
    service: InventoryServiceDep,
    session: DbSession,
    _auth: CurrentUser,
) -> VehicleResponse:
    """Purchase a quantity of a vehicle. Any authenticated user."""
    vehicle = service.purchase(vehicle_id, quantity=body.quantity)
    session.commit()
    session.refresh(vehicle)
    return VehicleResponse.model_validate(vehicle)


@router.post("/{vehicle_id}/restock", response_model=VehicleResponse)
def restock(
    vehicle_id: int,
    body: QuantityRequest,
    service: InventoryServiceDep,
    session: DbSession,
    _auth: AdminUser,
) -> VehicleResponse:
    """Restock a vehicle. Admin only."""
    vehicle = service.restock(vehicle_id, quantity=body.quantity)
    session.commit()
    session.refresh(vehicle)
    return VehicleResponse.model_validate(vehicle)
