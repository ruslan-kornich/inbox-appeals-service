from tortoise import fields, timezone

from .enums import TicketStatus
from .mixins import CreatedUpdatedFieldsMixin, UUIDPrimaryKeyMixin


class Ticket(UUIDPrimaryKeyMixin, CreatedUpdatedFieldsMixin):
    """
    Citizen ticket (request).
    Mandatory fields: owner, text, status.
    Optional fields: staff_assignee, staff_comment.
    Additional requirement: store 'who changed' and 'when' for processed tickets.
    """

    owner = fields.ForeignKeyField(
        "models.User",
        related_name="owned_tickets",
        on_delete=fields.OnDelete.CASCADE,
        index=True,
    )
    text = fields.TextField()

    status = fields.CharEnumField(TicketStatus, default=TicketStatus.NEW, index=True)

    staff_assignee = fields.ForeignKeyField(
        "models.User",
        related_name="assigned_tickets",
        on_delete=fields.OnDelete.SET_NULL,
        null=True,
        index=True,  # staff work queues by assignee
    )
    staff_comment = fields.TextField(null=True)

    # "who changed and when" for processed tickets
    last_modified_by = fields.ForeignKeyField(
        "models.User",
        related_name="modified_tickets",
        on_delete=fields.OnDelete.SET_NULL,
        null=True,
        index=True,  # useful for staff performance queries
    )
    last_modified_at = fields.DatetimeField(null=True, index=True)

    class Meta:
        table = "service_ticket"
        # Composite indexes to speed up common filters:
        indexes = (
            ("status", "created_at"),  # admin analytics: status over time
            ("staff_assignee_id", "status"),
            ("owner_id", "created_at"),
        )

    def __str__(self) -> str:
        return f"Ticket<{self.id} {self.status}>"

    async def mark_modified(self, user: "User | None") -> None:
        """
        Set 'who and when' fields for any staff-driven change.
        Should be called in the service layer whenever STAFF updates the ticket.
        """
        self.last_modified_by = user
        self.last_modified_at = timezone.now()
