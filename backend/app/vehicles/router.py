"""Vehicles router: CRUD and search endpoints.

All endpoints require authentication.  DELETE is additionally restricted to
admins via the AdminUser dependency.  Write endpoints commit explicitly before
returning so the data is durable before the response is sent.
"""

from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.deps import AdminUser, CurrentUser, DbSession
from app.vehicles.models import Category
from app.vehicles.repository import VehicleRepository
from app.vehicles.schemas import VehicleRequest, VehicleResponse
from app.vehicles.service import VehicleService

router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])


def _build_service(session: DbSession) -> VehicleService:
    return VehicleService(repo=VehicleRepository(session))


VehicleServiceDep = Annotated[VehicleService, Depends(_build_service)]


@router.post("", response_model=VehicleResponse, status_code=201)
def create_vehicle(
    body: VehicleRequest,
    service: VehicleServiceDep,
    session: DbSession,
    _auth: CurrentUser,
) -> VehicleResponse:
    vehicle = service.create(
        make=body.make,
        model=body.model,
        category=body.category,
        price=body.price,
        quantity=body.quantity,
    )
    session.commit()
    session.refresh(vehicle)
    return VehicleResponse.model_validate(vehicle)


@router.get("", response_model=list[VehicleResponse])
def list_vehicles(service: VehicleServiceDep, _auth: CurrentUser) -> list[VehicleResponse]:
    return [VehicleResponse.model_validate(v) for v in service.list_all()]


@router.get("/search", response_model=list[VehicleResponse])
def search_vehicles(
    service: VehicleServiceDep,
    _auth: CurrentUser,
    make: Annotated[str | None, Query()] = None,
    model: Annotated[str | None, Query()] = None,
    category: Annotated[Category | None, Query()] = None,
    min_price: Annotated[Decimal | None, Query()] = None,
    max_price: Annotated[Decimal | None, Query()] = None,
) -> list[VehicleResponse]:
    vehicles = service.search(
        make=make, model=model, category=category, min_price=min_price, max_price=max_price
    )
    return [VehicleResponse.model_validate(v) for v in vehicles]


@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: int,
    body: VehicleRequest,
    service: VehicleServiceDep,
    session: DbSession,
    _auth: CurrentUser,
) -> VehicleResponse:
    vehicle = service.update(
        vehicle_id,
        make=body.make,
        model=body.model,
        category=body.category,
        price=body.price,
        quantity=body.quantity,
    )
    session.commit()
    session.refresh(vehicle)
    return VehicleResponse.model_validate(vehicle)


@router.delete("/{vehicle_id}", status_code=204)
def delete_vehicle(
    vehicle_id: int,
    service: VehicleServiceDep,
    session: DbSession,
    _auth: AdminUser,
) -> None:
    """Delete a vehicle. Admin only."""
    service.delete(vehicle_id)
    session.commit()