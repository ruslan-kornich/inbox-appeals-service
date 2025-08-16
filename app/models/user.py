from typing import TYPE_CHECKING

from tortoise import fields

from .enums import UserRole
from .mixins import CreatedUpdatedFieldsMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.citizen_profile import CitizenProfile
    from app.models.ticket import Ticket


class User(UUIDPrimaryKeyMixin, CreatedUpdatedFieldsMixin):
    """
    System user.
    ADMIN and STAFF are represented via the 'role' field; separate tables are unnecessary.
    """

    email = fields.CharField(max_length=255, unique=True, index=True)
    password_hash = fields.CharField(max_length=255)  # Store only hashed passwords
    role = fields.CharEnumField(UserRole, default=UserRole.USER, index=True)

    # Reverse relations (declared for type hints / IDE; created dynamically by Tortoise)
    citizen_profile: fields.ReverseRelation["CitizenProfile"]
    owned_tickets: fields.ReverseRelation["Ticket"]
    assigned_tickets: fields.ReverseRelation["Ticket"]
    modified_tickets: fields.ReverseRelation["Ticket"]

    class Meta:
        table = "auth_user"
        indexes = ("email", "role")

    def __str__(self) -> str:
        return f"User<{self.id} {self.email} {self.role}>"
