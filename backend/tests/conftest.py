"""Root test configuration.

The test engine uses TEST_DATABASE_URL when set (local development, so the
dev database is left untouched) and falls back to DATABASE_URL for CI, where
that variable already points at the dealership_test database.

Tables are created via Alembic (the same path as production) rather than
Base.metadata.create_all so that migration tests can verify round-trips
without diverging from the actual schema used by other tests.

The fixture performs a defensive cleanup before upgrade to handle leftover
Postgres state (enum types, stale alembic_version) from previous failed runs.
"""

import os
from collections.abc import Generator

import pytest
from alembic.config import Config
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session

from alembic import command


def _alembic_cfg(url: str) -> Config:
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", url)
    return cfg


def _clean_db(engine: Engine) -> None:
    """Drop all known application objects so upgrade starts from a blank slate.

    Required when a previous test session failed mid-migration and left Postgres
    enum types or tables behind.
    """
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS vehicles CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS category CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS role CASCADE"))


@pytest.fixture(scope="session")
def test_engine() -> Generator[Engine, None, None]:
    """Session-scoped engine: cleans DB, runs alembic upgrade head once,
    tears down with downgrade base."""
    url = os.environ.get("TEST_DATABASE_URL") or ""
    if not url:
        from app.core.config import get_settings

        url = get_settings().database_url

    engine = create_engine(url)
    _clean_db(engine)

    cfg = _alembic_cfg(url)
    command.upgrade(cfg, "head")
    yield engine
    command.downgrade(cfg, "base")
    engine.dispose()


@pytest.fixture()
def db_session(test_engine: Engine) -> Generator[Session, None, None]:
    """Transaction-scoped session that rolls back after each test."""
    with Session(test_engine) as session:
        session.begin()
        yield session
        session.rollback()
