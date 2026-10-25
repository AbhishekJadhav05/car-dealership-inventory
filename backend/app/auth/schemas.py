"""Pydantic schemas for the auth feature."""

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Public representation of a user returned by the API."""

    model_config = {"from_attributes": True}

    id: int
    email: str
    role: str
