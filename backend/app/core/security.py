"""Security adapters: PasswordHasher and TokenService.

Both classes wrap third-party libraries behind simple interfaces (Adapter
pattern) so the rest of the application never imports pwdlib or PyJWT directly.
"""

from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from app.core.config import Settings
from app.core.exceptions import InvalidToken


class PasswordHasher:
    """Adapter over pwdlib (argon2) that hashes and verifies passwords."""

    def __init__(self) -> None:
        self._handler = PasswordHash([Argon2Hasher()])

    def hash(self, password: str) -> str:
        return self._handler.hash(password)

    def verify(self, plain: str, hashed: str) -> bool:
        return self._handler.verify(plain, hashed)


class TokenService:
    """Adapter over PyJWT that creates and decodes access tokens."""

    def __init__(self, settings: Settings) -> None:
        self._secret = settings.jwt_secret
        self._algorithm = settings.jwt_algorithm
        self._expire_minutes = settings.access_token_expire_minutes

    def create_access_token(self, subject: str) -> str:
        expire = datetime.now(UTC) + timedelta(minutes=self._expire_minutes)
        payload: dict[str, str | datetime] = {"sub": subject, "exp": expire}
        token: str = jwt.encode(payload, self._secret, algorithm=self._algorithm)
        return token

    def decode_subject(self, token: str) -> str:
        """Decode the token and return the subject claim.

        Raises InvalidToken if the token is malformed, expired, or the
        signature does not match.
        """
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
            sub: str = payload["sub"]
            return sub
        except (jwt.PyJWTError, KeyError) as exc:
            raise InvalidToken from exc
