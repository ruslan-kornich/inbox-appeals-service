
from pydantic import BaseModel, EmailStr

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
