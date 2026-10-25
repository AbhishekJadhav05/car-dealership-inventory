"""Pydantic schemas for the vehicles feature."""

from decimal import Decimal

from pydantic import BaseModel, field_serializer

from app.vehicles.models import Category


class VehicleRequest(BaseModel):
    make: str
    model: str
    category: Category
    price: Decimal
    quantity: int


class VehicleResponse(BaseModel):
    """Public representation of a vehicle returned by the API.

    price is serialised as a JSON number (float, 2 d.p.) per the spec.
    category is serialised as its string value (e.g. "sedan").
    """

    model_config = {"from_attributes": True}

    id: int
    make: str
    model: str
    category: Category
    price: Decimal
    quantity: int

    @field_serializer("price")
    def _serialize_price(self, value: Decimal) -> float:
        return float(round(value, 2))


class QuantityRequest(BaseModel):
    quantity: int
