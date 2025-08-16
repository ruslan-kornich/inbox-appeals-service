from enum import Enum


class UserRole(str, Enum):
    """Application roles."""
    USER = "USER"
    STAFF = "STAFF"
    ADMIN = "ADMIN"


class TicketStatus(str, Enum):
    """Business lifecycle for a ticket."""
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"
