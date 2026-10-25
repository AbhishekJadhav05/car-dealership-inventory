"""Shared FastAPI dependencies injected into routers."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.repository import UserRepository
from app.auth.schemas import UserResponse
from app.core.config import get_settings
from app.core.exceptions import InvalidToken
from app.core.security import TokenService
from app.db.session import get_db

_bearer = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
    session: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    """Decode the Bearer token and return the authenticated user.

    Raises HTTP 401 if the token is missing, malformed, expired, or the
    user referenced by the token no longer exists.
    """
    token_service = TokenService(get_settings())
    try:
        user_id = int(token_service.decode_subject(credentials.credentials))
    except (InvalidToken, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from None

    user = UserRepository(session).get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return UserResponse.model_validate(user)


CurrentUser = Annotated[UserResponse, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]
