"""Auth router: /api/auth/register, /api/auth/login, /api/auth/me."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth.repository import UserRepository
from app.auth.schemas import LoginRequest, LoginResponse, RegisterRequest, UserResponse
from app.auth.service import AuthService
from app.core.config import get_settings
from app.core.deps import CurrentUser, DbSession
from app.core.security import PasswordHasher, TokenService

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _build_service(session: DbSession) -> AuthService:
    """Construct an AuthService with all its concrete dependencies."""
    return AuthService(
        repo=UserRepository(session),
        hasher=PasswordHasher(),
        token_service=TokenService(get_settings()),
    )


AuthServiceDep = Annotated[AuthService, Depends(_build_service)]


@router.post("/register", response_model=UserResponse, status_code=201)
def register(body: RegisterRequest, service: AuthServiceDep) -> UserResponse:
    """Register a new customer account.

    Returns 409 if the email is already taken (handled by the global
    UserAlreadyExists exception handler in create_app).
    """
    user = service.register(email=body.email, password=body.password)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, service: AuthServiceDep) -> LoginResponse:
    """Authenticate and return a signed JWT.

    Returns 401 on wrong password or unknown email (handled globally).
    """
    return service.login(email=body.email, password=body.password)


@router.get("/me", response_model=UserResponse)
def me(current_user: CurrentUser) -> UserResponse:
    """Return the profile of the currently authenticated user."""
    return current_user
