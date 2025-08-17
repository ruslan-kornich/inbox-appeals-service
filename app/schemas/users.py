from typing import Generic, TypeVar

from pydantic import BaseModel, EmailStr, ConfigDict

from app.models import UserRole


class UserShort(BaseModel):
    """Minimal user info for lightweight responses."""
    id: str
    email: EmailStr
    role: UserRole


class CreateStaffBody(BaseModel):
    """Admin creates a staff account."""
    email: EmailStr
    password: str


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response model for list endpoints.
    """
    # Enable ORM attribute reading if you pass ORM objects to nested models
    model_config = ConfigDict(from_attributes=True)

    total: int
    page: int
    size: int
    items: list[T]
