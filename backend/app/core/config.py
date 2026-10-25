"""Application configuration, loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Typed settings. Field names map to upper-case environment variables."""

    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
