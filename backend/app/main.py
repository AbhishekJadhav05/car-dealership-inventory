"""FastAPI application factory."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.auth.router import router as auth_router
from app.core.exceptions import InvalidCredentials, UserAlreadyExists


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    All domain-exception-to-HTTP mappings live here so routers stay clean.
    """
    app = FastAPI(title="Car Dealership Inventory API", version="0.1.0")

    @app.exception_handler(UserAlreadyExists)
    async def _user_already_exists(request: Request, exc: UserAlreadyExists) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": "Email already registered"})

    @app.exception_handler(InvalidCredentials)
    async def _invalid_credentials(request: Request, exc: InvalidCredentials) -> JSONResponse:
        return JSONResponse(status_code=401, content={"detail": "Invalid credentials"})

    app.include_router(auth_router)

    return app
