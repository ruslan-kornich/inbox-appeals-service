
from typing import Generic, TypeVar

from pydantic import BaseModel, EmailStr
from pydantic.generics import GenericModel

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

class PaginatedResponse(GenericModel, Generic[T]):
    total: int
    page: int
    size: int
    items: list[T]
