"""Alembic environment configuration.

The database URL is read from Settings (env / .env file) at runtime.
Tests override it by calling cfg.set_main_option("sqlalchemy.url", ...) before
running upgrade/downgrade commands.
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

# Import every model module so their tables are registered in Base.metadata.
import app.auth.models
import app.vehicles.models  # noqa: F401
from alembic import context
from app.db.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _get_url() -> str:
    """Return the DB URL from alembic.ini (set programmatically by tests)
    or fall back to the application settings."""
    url = config.get_main_option("sqlalchemy.url")
    if url:
        return url
    from app.core.config import get_settings

    return get_settings().database_url


def run_migrations_offline() -> None:
    context.configure(
        url=_get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = _get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
