"""Fixtures for API (end-to-end) tests.

The TestClient is wired to a transaction-scoped database session via
dependency override, so each test is isolated and leaves no data behind.
"""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import create_app


@pytest.fixture()
def client(test_engine: Engine) -> Generator[TestClient, None, None]:
    """TestClient whose DB session is rolled back after each test."""
    with Session(test_engine) as session:
        session.begin()
        app = create_app()
        app.dependency_overrides[get_db] = lambda: session
        yield TestClient(app)
        session.rollback()
