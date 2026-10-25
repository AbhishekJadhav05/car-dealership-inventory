"""Integration tests for UserRepository against a real Postgres database.

These tests use the db_session fixture from integration/conftest.py, which
wraps every test in a transaction that is rolled back — no data leaks between
tests and no truncation is needed.
"""

import pytest
from sqlalchemy.orm import Session

from app.auth.models import Role
from app.auth.repository import UserRepository


@pytest.fixture()
def repo(db_session: Session) -> UserRepository:
    return UserRepository(db_session)


def test_create_persists_user_and_returns_id(repo: UserRepository) -> None:
    user = repo.create(email="alice@example.com", hashed_password="hashed")

    assert user.id is not None
    assert user.email == "alice@example.com"
    assert user.role == Role.customer


def test_get_by_email_finds_existing_user(repo: UserRepository) -> None:
    repo.create(email="alice@example.com", hashed_password="hashed")

    found = repo.get_by_email("alice@example.com")

    assert found is not None
    assert found.email == "alice@example.com"


def test_get_by_email_returns_none_for_unknown_email(repo: UserRepository) -> None:
    result = repo.get_by_email("nobody@example.com")

    assert result is None
