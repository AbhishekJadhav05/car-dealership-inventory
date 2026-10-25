"""SQLAlchemy session factory and FastAPI get_db dependency."""

from collections.abc import Generator
from functools import cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from app.core.config import get_settings


@cache
def _get_engine() -> Engine:
    """Create the SQLAlchemy engine once and reuse it for the process lifetime.

    functools.cache makes this a lazy singleton — the engine is not created at
    import time, so importing this module in tests does not require a running
    database.
    """
    return create_engine(get_settings().database_url)


def get_db() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session and roll back on error.

    Handlers commit explicitly before returning, so the response is never sent
    before the data is committed.  FastAPI calls this as a generator dependency
    for every request.  Tests override it via app.dependency_overrides so the
    real engine is never touched during the test suite.
    """
    with Session(_get_engine()) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
