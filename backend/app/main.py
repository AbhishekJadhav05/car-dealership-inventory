
"""FastAPI application factory."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.auth.router import router as auth_router
from app.core.exceptions import (
    InvalidCredentials,
    OutOfStock,
    UserAlreadyExists,
    VehicleNotFound,
)
from app.inventory.router import router as inventory_router
from app.vehicles.router import router as vehicles_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    All domain-exception-to-HTTP mappings live here so routers stay clean.
    """
    app = FastAPI(title="Car Dealership Inventory API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ------------------------------------------------------------------ auth
    @app.exception_handler(UserAlreadyExists)
    async def _user_already_exists(
        request: Request, exc: UserAlreadyExists
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"detail": "Email already registered"},
        )

    @app.exception_handler(InvalidCredentials)
    async def _invalid_credentials(
        request: Request, exc: InvalidCredentials
    ) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid credentials"},
        )

    # --------------------------------------------------------------- vehicles
    @app.exception_handler(VehicleNotFound)
    async def _vehicle_not_found(
        request: Request, exc: VehicleNotFound
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"detail": "Vehicle not found"},
        )

    @app.exception_handler(OutOfStock)
    async def _out_of_stock(
        request: Request, exc: OutOfStock
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"detail": "Insufficient stock"},
        )

    app.include_router(auth_router)
    app.include_router(vehicles_router)
    app.include_router(inventory_router)

    return app
