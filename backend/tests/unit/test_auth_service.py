"""Unit tests for AuthService.

All tests use InMemoryUserRepository — no database involved.  The service
receives its dependencies through the constructor (constructor injection),
which makes substituting fakes trivial.
"""

import pytest

from app.auth.models import Role
from app.auth.service import AuthService
from app.core.config import Settings
from app.core.exceptions import InvalidCredentials, UserAlreadyExists
from app.core.security import PasswordHasher, TokenService
from tests.unit.fakes import InMemoryUserRepository


@pytest.fixture()
def settings(monkeypatch: pytest.MonkeyPatch) -> Settings:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost:5433/db")
    monkeypatch.setenv("JWT_SECRET", "unit-test-secret")
    return Settings(_env_file=None)


@pytest.fixture()
def repo() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture()
def service(repo: InMemoryUserRepository, settings: Settings) -> AuthService:
    return AuthService(
        repo=repo,
        hasher=PasswordHasher(),
        token_service=TokenService(settings),
    )


# ---------------------------------------------------------------------------
# register
# ---------------------------------------------------------------------------


def test_register_creates_a_customer(service: AuthService, repo: InMemoryUserRepository) -> None:
    user = service.register(email="alice@example.com", password="secret123")

    assert user.email == "alice@example.com"
    assert user.role == Role.customer
    assert repo.get_by_email("alice@example.com") is not None


def test_register_stores_hashed_password(
    service: AuthService, repo: InMemoryUserRepository
) -> None:
    service.register(email="alice@example.com", password="secret123")

    stored = repo.get_by_email("alice@example.com")
    assert stored is not None
    assert stored.hashed_password != "secret123"


def test_register_raises_on_duplicate_email(service: AuthService) -> None:
    service.register(email="alice@example.com", password="secret123")

    with pytest.raises(UserAlreadyExists):
        service.register(email="alice@example.com", password="other")


# ---------------------------------------------------------------------------
# login
# ---------------------------------------------------------------------------


def test_login_returns_bearer_token(service: AuthService) -> None:
    service.register(email="alice@example.com", password="secret123")

    result = service.login(email="alice@example.com", password="secret123")

    assert result.access_token
    assert result.token_type == "bearer"


def test_login_raises_on_wrong_password(service: AuthService) -> None:
    service.register(email="alice@example.com", password="secret123")

    with pytest.raises(InvalidCredentials):
        service.login(email="alice@example.com", password="wrong")


def test_login_raises_on_unknown_email(service: AuthService) -> None:
    with pytest.raises(InvalidCredentials):
        service.login(email="nobody@example.com", password="secret123")
