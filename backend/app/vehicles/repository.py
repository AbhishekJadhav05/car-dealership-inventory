"""VehicleRepository: Protocol and SQLAlchemy implementation."""

from decimal import Decimal
from typing import Protocol

from sqlalchemy import ColumnElement, and_, select
from sqlalchemy import update as sa_update
from sqlalchemy.orm import Session

from app.vehicles.models import Category, Vehicle


class VehicleRepositoryProtocol(Protocol):
    """Interface that every vehicle repository must satisfy."""

    def create(
        self,
        make: str,
        model: str,
        category: Category,
        price: Decimal,
        quantity: int,
    ) -> Vehicle: ...

    def get_by_id(self, vehicle_id: int) -> Vehicle | None: ...

    def list_all(self) -> list[Vehicle]: ...

    def search(
        self,
        *,
        make: str | None = ...,
        model: str | None = ...,
        category: Category | None = ...,
        min_price: Decimal | None = ...,
        max_price: Decimal | None = ...,
    ) -> list[Vehicle]: ...

    def update(self, vehicle_id: int, **fields: object) -> Vehicle | None: ...

    def delete(self, vehicle_id: int) -> bool: ...

    def atomic_purchase(self, vehicle_id: int, quantity: int) -> Vehicle | None: ...

    def restock(self, vehicle_id: int, quantity: int) -> Vehicle | None: ...


class VehicleRepository:
    """SQLAlchemy implementation of VehicleRepositoryProtocol."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        make: str,
        model: str,
        category: Category,
        price: Decimal,
        quantity: int,
    ) -> Vehicle:
        vehicle = Vehicle(make=make, model=model, category=category, price=price, quantity=quantity)
        self._session.add(vehicle)
        self._session.flush()
        return vehicle

    def get_by_id(self, vehicle_id: int) -> Vehicle | None:
        return self._session.get(Vehicle, vehicle_id)

    def list_all(self) -> list[Vehicle]:
        return list(self._session.scalars(select(Vehicle)).all())

    def search(
        self,
        *,
        make: str | None = None,
        model: str | None = None,
        category: Category | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
    ) -> list[Vehicle]:
        conditions: list[ColumnElement[bool]] = []
        if make is not None:
            conditions.append(Vehicle.make.ilike(f"%{make}%"))
        if model is not None:
            conditions.append(Vehicle.model.ilike(f"%{model}%"))
        if category is not None:
            conditions.append(Vehicle.category == category)
        if min_price is not None:
            conditions.append(Vehicle.price >= min_price)
        if max_price is not None:
            conditions.append(Vehicle.price <= max_price)
        stmt = select(Vehicle)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        return list(self._session.scalars(stmt).all())

    def update(self, vehicle_id: int, **fields: object) -> Vehicle | None:
        vehicle = self.get_by_id(vehicle_id)
        if vehicle is None:
            return None
        for key, value in fields.items():
            setattr(vehicle, key, value)
        self._session.flush()
        return vehicle

    def delete(self, vehicle_id: int) -> bool:
        vehicle = self.get_by_id(vehicle_id)
        if vehicle is None:
            return False
        self._session.delete(vehicle)
        self._session.flush()
        return True

    def atomic_purchase(self, vehicle_id: int, quantity: int) -> Vehicle | None:
        """Decrease quantity atomically using a single UPDATE with a WHERE guard.

        Returns the updated vehicle on success, None if the vehicle does not
        exist or has insufficient stock (rowcount == 0 covers both cases).
        """
        stmt = (
            sa_update(Vehicle)
            .where(Vehicle.id == vehicle_id, Vehicle.quantity >= quantity)
            .values(quantity=Vehicle.quantity - quantity)
            .execution_options(synchronize_session=False)
        )
        result = self._session.execute(stmt)
        if result.rowcount == 0:  # type: ignore[attr-defined]
            return None
        # Expire the identity-map entry so the next get() re-fetches from DB.
        vehicle = self._session.get(Vehicle, vehicle_id)
        if vehicle is not None:
            self._session.expire(vehicle)
        return self._session.get(Vehicle, vehicle_id)

    def restock(self, vehicle_id: int, quantity: int) -> Vehicle | None:
        vehicle = self.get_by_id(vehicle_id)
        if vehicle is None:
            return None
        vehicle.quantity += quantity
        self._session.flush()
        return vehicle
