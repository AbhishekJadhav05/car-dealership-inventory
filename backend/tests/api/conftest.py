"""Fixtures for API (end-to-end) tests.

All fixtures share one rolled-back session per test so data created by
helper fixtures (e.g. admin_headers) is visible to the TestClient without
being committed to the database.
"""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from app.auth.models import Role
from app.auth.repository import UserRepository
from app.core.security import PasswordHasher
from app.db.session import get_db
from app.main import create_app

_PASSWORD = "Pass123!"


@pytest.fixture()
def db_session(test_engine: Engine) -> Generator[Session, None, None]:
    """Transaction-scoped session shared by the client and all helper fixtures."""
    with Session(test_engine) as session:
        session.begin()
        yield session
        session.rollback()


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    """TestClient wired to the rolled-back test session."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: db_session
    return TestClient(app)


@pytest.fixture()
def customer_headers(client: TestClient, db_session: Session) -> dict[str, str]:
    """Register a customer and return Bearer auth headers."""
    repo = UserRepository(db_session)
    repo.create(email="customer@test.com", hashed_password=PasswordHasher().hash(_PASSWORD))
    db_session.flush()
    resp = client.post(
        "/api/auth/login",
        json={"email": "customer@test.com", "password": _PASSWORD},
    )
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture()
def admin_headers(client: TestClient, db_session: Session) -> dict[str, str]:
    """Create an admin user directly (bypassing register which only makes customers)."""
    repo = UserRepository(db_session)
    repo.create(
        email="admin@test.com",
        hashed_password=PasswordHasher().hash(_PASSWORD),
        role=Role.admin,
    )
    db_session.flush()
    resp = client.post("/api/auth/login", json={"email": "admin@test.com", "password": _PASSWORD})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture()
def vehicle_payload() -> dict[str, object]:
    """Minimal valid vehicle body for POST /api/vehicles."""
    return {
        "make": "Toyota",
        "model": "Camry",
        "category": "sedan",
        "price": 25000.00,
        "quantity": 5,
    }


@pytest.fixture()
def created_vehicle(
    client: TestClient,
    customer_headers: dict[str, str],
    vehicle_payload: dict[str, object],
) -> dict[str, object]:
    """A vehicle that has been created via the API; used by update/delete/inventory tests."""
    resp = client.post("/api/vehicles", json=vehicle_payload, headers=customer_headers)
    result: dict[str, object] = resp.json()
    return result
