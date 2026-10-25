"""Root test configuration.

The test engine uses TEST_DATABASE_URL when set (local development, so the
dev database is left untouched) and falls back to DATABASE_URL for CI, where
that variable already points at the dealership_test database.
"""

import os
from collections.abc import Generator

import pytest
from sqlalchemy import Engine, create_engine

from app.core.config import get_settings
from app.db.base import Base


@pytest.fixture(scope="session")
def test_engine() -> Generator[Engine, None, None]:
    """Session-scoped engine: creates all tables once, drops them on teardown."""
    url = os.environ.get("TEST_DATABASE_URL") or get_settings().database_url
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
