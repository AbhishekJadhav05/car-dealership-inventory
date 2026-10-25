"""UserRepository: Protocol and SQLAlchemy implementation.

The Protocol defines the interface that AuthService depends on.  The concrete
UserRepository class satisfies it and is used in production.  Unit tests use
InMemoryUserRepository (tests/unit/fakes.py), which also satisfies the Protocol
via structural subtyping — no explicit registration needed.
"""

from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.models import Role, User


class UserRepositoryProtocol(Protocol):
    """Interface that every user repository must satisfy."""

    def create(self, email: str, hashed_password: str, role: Role = ...) -> User: ...

    def get_by_email(self, email: str) -> User | None: ...

    def get_by_id(self, user_id: int) -> User | None: ...


class UserRepository:
    """SQLAlchemy implementation of UserRepositoryProtocol."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, email: str, hashed_password: str, role: Role = Role.customer) -> User:
        """Persist a new user and return it with its database-assigned id."""
        user = User(email=email, hashed_password=hashed_password, role=role)
        self._session.add(user)
        self._session.flush()  # populate id from the DB sequence without committing
        return user

    def get_by_email(self, email: str) -> User | None:
        return self._session.scalar(select(User).where(User.email == email))

    def get_by_id(self, user_id: int) -> User | None:
        return self._session.get(User, user_id)
