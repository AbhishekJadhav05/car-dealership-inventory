"""In-memory fakes used by unit tests.

These implement the same Protocols as the real repositories but store data in
plain dicts — no database, no SQLAlchemy session.  They let unit tests run
fast and without any infrastructure.
"""

from decimal import Decimal

from app.auth.models import Role, User
from app.vehicles.models import Category, Vehicle


class InMemoryUserRepository:
    """Fake UserRepository backed by a dict.

    Ids are auto-incremented integers starting at 1, matching the behaviour
    of the real Postgres sequence.
    """

    def __init__(self) -> None:
        self._store: dict[str, User] = {}  # keyed by email for O(1) lookups
        self._next_id: int = 1

    def create(self, email: str, hashed_password: str, role: Role = Role.customer) -> User:
        user = User(id=self._next_id, email=email, hashed_password=hashed_password, role=role)
        self._store[email] = user
        self._next_id += 1
        return user

    def get_by_email(self, email: str) -> User | None:
        return self._store.get(email)

    def get_by_id(self, user_id: int) -> User | None:
        return next((u for u in self._store.values() if u.id == user_id), None)


class InMemoryVehicleRepository:
    """Fake VehicleRepository backed by a dict.

    atomic_purchase mirrors the real SQL semantics: returns the updated vehicle
    when sufficient stock exists, None otherwise.
    """

    def __init__(self) -> None:
        self._store: dict[int, Vehicle] = {}
        self._next_id: int = 1

    def create(
        self,
        make: str,
        model: str,
        category: Category,
        price: Decimal,
        quantity: int,
    ) -> Vehicle:
        vehicle = Vehicle(
            id=self._next_id,
            make=make,
            model=model,
            category=category,
            price=price,
            quantity=quantity,
        )
        self._store[self._next_id] = vehicle
        self._next_id += 1
        return vehicle

    def get_by_id(self, vehicle_id: int) -> Vehicle | None:
        return self._store.get(vehicle_id)

    def list_all(self) -> list[Vehicle]:
        return list(self._store.values())

    def search(
        self,
        *,
        make: str | None = None,
        model: str | None = None,
        category: Category | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
    ) -> list[Vehicle]:
        results = list(self._store.values())
        if make is not None:
            results = [v for v in results if make.lower() in v.make.lower()]
        if model is not None:
            results = [v for v in results if model.lower() in v.model.lower()]
        if category is not None:
            results = [v for v in results if v.category == category]
        if min_price is not None:
            results = [v for v in results if v.price >= min_price]
        if max_price is not None:
            results = [v for v in results if v.price <= max_price]
        return results

    def update(self, vehicle_id: int, **fields: object) -> Vehicle | None:
        vehicle = self._store.get(vehicle_id)
        if vehicle is None:
            return None
        for key, value in fields.items():
            setattr(vehicle, key, value)
        return vehicle

    def delete(self, vehicle_id: int) -> bool:
        if vehicle_id not in self._store:
            return False
        del self._store[vehicle_id]
        return True

    def atomic_purchase(self, vehicle_id: int, quantity: int) -> Vehicle | None:
        """Decrease quantity atomically; return the vehicle or None if out of stock."""
        vehicle = self._store.get(vehicle_id)
        if vehicle is None or vehicle.quantity < quantity:
            return None
        vehicle.quantity -= quantity
        return vehicle

    def restock(self, vehicle_id: int, quantity: int) -> Vehicle | None:
        vehicle = self._store.get(vehicle_id)
        if vehicle is None:
            return None
        vehicle.quantity += quantity
        return vehicle
