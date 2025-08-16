from .citizen_profile import CitizenProfile
from .enums import TicketStatus, UserRole
from .mixins import CreatedUpdatedFieldsMixin, UUIDPrimaryKeyMixin
from .ticket import Ticket
from .user import User

__all__ = [
    "CitizenProfile",
    "CreatedUpdatedFieldsMixin",
    "Ticket",
    "TicketStatus",
    "UUIDPrimaryKeyMixin",
    "User",
    "UserRole",
]

# Use this list in Tortoise.init to register models:
MODELS_MODULES = [
    "app.models.user",
    "app.models.citizen_profile",
    "app.models.ticket",
]
