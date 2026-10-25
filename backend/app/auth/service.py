"""AuthService: business logic for user registration and login.

Depends on UserRepositoryProtocol so unit tests can inject an in-memory fake
without touching the database (Dependency Inversion).  The concrete adapters
(PasswordHasher, TokenService) are also injected — no hidden imports.
"""

from app.auth.models import User
from app.auth.repository import UserRepositoryProtocol
from app.auth.schemas import LoginResponse
from app.core.exceptions import InvalidCredentials, UserAlreadyExists
from app.core.security import PasswordHasher, TokenService


class AuthService:
    """Facade that orchestrates registration and login.

    Register: validate uniqueness -> hash password -> persist.
    Login: look up user -> verify password -> issue JWT.
    """

    def __init__(
        self,
        repo: UserRepositoryProtocol,
        hasher: PasswordHasher,
        token_service: TokenService,
    ) -> None:
        self._repo = repo
        self._hasher = hasher
        self._token_service = token_service

    def register(self, email: str, password: str) -> User:
        """Create a new customer account.

        Raises UserAlreadyExists when the email is already taken.
        """
        if self._repo.get_by_email(email) is not None:
            raise UserAlreadyExists(email)
        hashed = self._hasher.hash(password)
        return self._repo.create(email=email, hashed_password=hashed)

    def login(self, email: str, password: str) -> LoginResponse:
        """Verify credentials and return a signed JWT.

        Raises InvalidCredentials for both unknown emails and wrong passwords
        (same error, to avoid user enumeration).
        """
        user = self._repo.get_by_email(email)
        if user is None or not self._hasher.verify(password, user.hashed_password):
            raise InvalidCredentials
        token = self._token_service.create_access_token(subject=str(user.id))
        return LoginResponse(access_token=token)
