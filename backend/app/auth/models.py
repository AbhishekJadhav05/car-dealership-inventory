"""SQLAlchemy models for the auth feature."""

import enum

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Role(enum.Enum):
    customer = "customer"
    admin = "admin"


class User(Base):
    """Represents a registered user.

    Roles are stored as a Postgres enum.  Registration always creates
    customers; admins are promoted via a seed script or env bootstrap.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(SQLEnum(Role), nullable=False, default=Role.customer)
