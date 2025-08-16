
from tortoise import fields
from .mixins import UUIDPrimaryKeyMixin, CreatedUpdatedFieldsMixin
from .enums import UserRole


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
        # email already has unique & index; role is indexed for admin/staff queries
        indexes = ("email", "role")

    def __str__(self) -> str:
        return f"User<{self.id} {self.email} {self.role}>"
