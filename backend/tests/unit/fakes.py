"""In-memory fakes used by unit tests.

These implement the same Protocols as the real repositories but store data in
plain dicts — no database, no SQLAlchemy session.  They let unit tests run
fast and without any infrastructure.
"""

from app.auth.models import Role, User


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
