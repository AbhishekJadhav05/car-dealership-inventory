import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_load_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost:5433/db")
    monkeypatch.setenv("JWT_SECRET", "test-secret")

    settings = Settings(_env_file=None)

    assert settings.database_url == "postgresql+psycopg://u:p@localhost:5433/db"
    assert settings.jwt_secret == "test-secret"


def test_settings_have_sensible_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost:5433/db")
    monkeypatch.setenv("JWT_SECRET", "test-secret")

    settings = Settings(_env_file=None)

    assert settings.jwt_algorithm == "HS256"
    assert settings.access_token_expire_minutes == 60


@pytest.mark.parametrize("missing_field", ["DATABASE_URL", "JWT_SECRET"])
def test_settings_require_field(monkeypatch: pytest.MonkeyPatch, missing_field: str) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost:5433/db")
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.delenv(missing_field, raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
