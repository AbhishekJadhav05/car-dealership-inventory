"""SQLAlchemy models for the vehicles feature."""

import enum
from decimal import Decimal

from sqlalchemy import CheckConstraint, Integer, Numeric, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Category(enum.Enum):
    sedan = "sedan"
    suv = "suv"
    truck = "truck"
    van = "van"
    coupe = "coupe"
    hatchback = "hatchback"
    convertible = "convertible"
    pickup = "pickup"


class Vehicle(Base):
    """Represents a vehicle in the dealership inventory.

    price is stored as NUMERIC(10, 2) for exact decimal arithmetic.
    quantity is guarded by a DB-level CHECK so it can never go negative
    even if application logic has a bug.
    """

    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    make: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    model: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category: Mapped[Category] = mapped_column(SQLEnum(Category), nullable=False, index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_vehicles_quantity_non_negative"),
        CheckConstraint("price > 0", name="ck_vehicles_price_positive"),
    )
