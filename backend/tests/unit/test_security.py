"""Unit tests for PasswordHasher and TokenService adapters.

These tests have no database dependency.  TokenService is constructed with a
Settings instance built from monkeypatched env vars so no real .env is read.
"""

import pytest

from app.core.config import Settings
from app.core.security import PasswordHasher, TokenService

# ---------------------------------------------------------------------------
# PasswordHasher
# ---------------------------------------------------------------------------


def test_password_hasher_hashes_and_verifies() -> None:
    hasher = PasswordHasher()
    hashed = hasher.hash("secret123")

    assert hasher.verify("secret123", hashed)


def test_password_hasher_rejects_wrong_password() -> None:
    hasher = PasswordHasher()
    hashed = hasher.hash("secret123")

    assert not hasher.verify("wrong", hashed)


# ---------------------------------------------------------------------------
# TokenService
# ---------------------------------------------------------------------------


@pytest.fixture()
def token_service(monkeypatch: pytest.MonkeyPatch) -> TokenService:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost:5433/db")
    monkeypatch.setenv("JWT_SECRET", "unit-test-secret")
    settings = Settings(_env_file=None)
    return TokenService(settings)


def test_token_service_encodes_and_decodes(token_service: TokenService) -> None:
    token = token_service.create_access_token(subject="user-42")

    assert token_service.decode_subject(token) == "user-42"


def test_token_service_raises_on_invalid_token(token_service: TokenService) -> None:
    # Exception tightened to InvalidToken in the green step once app.core.exceptions exists.
    with pytest.raises(Exception):  # noqa: B017
        token_service.decode_subject("not.a.valid.token")
