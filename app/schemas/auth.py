
from datetime import date

from pydantic import BaseModel, EmailStr, Field


class RegisterUserBody(BaseModel):
    """Registration payload for USER with required citizen profile fields."""

    email: EmailStr
    password: str = Field(min_length=6)
    inn: str
    phone: str
    first_name: str
    last_name: str
    middle_name: str | None = None
    birth_date: date


class LoginBody(BaseModel):
    """Login with email and password."""

    email: EmailStr
    password: str


class AccessTokenResponse(BaseModel):
    """Returned access token."""

    access_token: str
    token_type: str = "bearer"
