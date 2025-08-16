from .enums import UserRole, TicketStatus
from .mixins import UUIDPrimaryKeyMixin, CreatedUpdatedFieldsMixin
from .user import User
from .citizen_profile import CitizenProfile
from .ticket import Ticket

__all__ = [
    "UserRole",
    "TicketStatus",
    "UUIDPrimaryKeyMixin",
    "CreatedUpdatedFieldsMixin",
    "User",
    "CitizenProfile",
    "Ticket",
]

# Use this list in Tortoise.init to register models:
MODELS_MODULES = [
    "app.models.user",
    "app.models.citizen_profile",
    "app.models.ticket",
]
