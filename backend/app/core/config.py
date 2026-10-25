"""Application configuration, loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed settings. Field names map to upper-case environment variables.

    extra="ignore" lets the .env file contain keys like TEST_DATABASE_URL
    without causing a validation error.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings singleton.

    lru_cache ensures the .env file is read only once per process.
    Call get_settings.cache_clear() in tests that need a fresh instance.
    """
    return Settings()
