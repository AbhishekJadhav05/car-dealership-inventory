"""Migration tests: verify that Alembic upgrade and downgrade run cleanly.

Run as part of the full suite — the restore_schema fixture ensures subsequent
test modules (test_user_repository, test_vehicle_repository) still have tables.
"""

import os
from collections.abc import Generator

import pytest
from alembic.config import Config
from sqlalchemy import Engine, inspect, text

from alembic import command
from app.core.config import get_settings


@pytest.fixture(scope="module")
def alembic_cfg(test_engine: Engine) -> Config:
    url = os.environ.get("TEST_DATABASE_URL") or get_settings().database_url
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", url)
    return cfg


@pytest.fixture(scope="module", autouse=True)
def clean_and_restore(alembic_cfg: Config, test_engine: Engine) -> Generator[None, None, None]:
    """Drop all tables before this module, restore them after.

    Before: wipes the session-scoped upgrade so we start from a blank slate.
    After:  re-applies upgrade so subsequent integration test modules work.
    """
    with test_engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS category CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS role CASCADE"))
    from app.db.base import Base

    Base.metadata.drop_all(test_engine)

    yield  # run test_upgrade and test_downgrade

    command.upgrade(alembic_cfg, "head")  # restore for tests that run after this module


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
