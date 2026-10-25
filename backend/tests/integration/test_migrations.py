"""Migration tests: verify that Alembic upgrade and downgrade run cleanly.

These tests are intentionally run in isolation from the rest of the integration
suite because they drop and recreate tables.  Run with:

    pytest tests/integration/test_migrations.py -v

The test_engine fixture (session-scoped) uses Base.metadata.create_all/drop_all.
These tests use Alembic directly so we can verify the migration path that
production uses.  In the green step, tests/conftest.py will be updated to use
alembic upgrade head instead of metadata.create_all, making this the canonical
table-creation path for all tests.
"""

import os

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, inspect, text

from app.core.config import get_settings


@pytest.fixture(scope="module")
def alembic_cfg() -> Config:
    cfg = Config("alembic.ini")
    url = os.environ.get("TEST_DATABASE_URL") or get_settings().database_url
    cfg.set_main_option("sqlalchemy.url", url)
    return cfg


@pytest.fixture(scope="module", autouse=True)
def clean_schema(alembic_cfg: Config, test_engine: Engine) -> None:
    """Drop everything before migration tests so we start from a blank slate."""
    with test_engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
    from app.db.base import Base

    Base.metadata.drop_all(test_engine)


def test_upgrade_creates_users_and_vehicles_tables(
    alembic_cfg: Config, test_engine: Engine
) -> None:
    command.upgrade(alembic_cfg, "head")

    tables = inspect(test_engine).get_table_names()
    assert "users" in tables
    assert "vehicles" in tables


def test_downgrade_removes_all_application_tables(alembic_cfg: Config, test_engine: Engine) -> None:
    command.downgrade(alembic_cfg, "base")

    tables = inspect(test_engine).get_table_names()
    assert "users" not in tables
    assert "vehicles" not in tables
