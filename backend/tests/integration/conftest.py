"""Fixtures for integration tests.

Each test runs inside a transaction that is rolled back on teardown, so
tests are fully isolated and the database is left clean between runs.
"""

from collections.abc import Generator

import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session


@pytest.fixture()
def db_session(test_engine: Engine) -> Generator[Session, None, None]:
    """Yield a session whose transaction is rolled back after each test."""
    with Session(test_engine) as session:
        session.begin()
        yield session
        session.rollback()
