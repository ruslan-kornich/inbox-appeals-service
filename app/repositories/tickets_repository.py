from collections.abc import Iterable

from tortoise import timezone
from tortoise.backends.base.client import BaseDBAsyncClient

from app.models import Ticket, TicketStatus, User

from .base import BaseRepository


class TicketRepository(BaseRepository[Ticket]):
    """
    Repository for Ticket with domain-specific helpers for the mandatory scope.
    """

    def __init__(self) -> None:
        # BaseRepository now only expects the model class.
        super().__init__(model=Ticket)

    async def list_by_owner(
            self,
            owner_id: str,
            *,
            only_fields: Iterable[str] | None = None,
            using_db: BaseDBAsyncClient | None = None,
    ) -> list[Ticket]:
        """
        List tickets belonging to the given owner, newest first.

        If 'only_fields' is provided, the query will select only these fields.
        """
        # Build QuerySet manually to support optional .only(*fields)
        qs = self.model.filter(owner_id=owner_id).order_by("-created_at")
        if using_db is not None:
            qs = qs.using_db(using_db)

        # For typical read screens we want a few helpful relations preloaded.
        qs = qs.select_related("staff_assignee", "last_modified_by")

        if only_fields:
            qs = qs.only(*only_fields)

        return await qs

    async def list_for_staff_queue(
            self,
            *,
            statuses: list[TicketStatus] | None = None,
            assignee_id: str | None = None,
            using_db: BaseDBAsyncClient | None = None,
    ) -> list[Ticket]:
        """
        List tickets for staff processing.
        If 'assignee_id' is provided, returns the staff member's own queue.
        """
        filters: dict[str, object] = {}
        if statuses:
            filters["status__in"] = statuses
        if assignee_id is not None:
            filters["staff_assignee_id"] = assignee_id

        # Use BaseRepository helper for consistency
        return await self.list_records(
            filters=filters or None,
            order_by=["status", "created_at"],
            select_related=["owner", "staff_assignee", "last_modified_by"],
            using_db=using_db,
        )

    async def update_status_with_audit(
            self,
            *,
            ticket_id: str,
            new_status: TicketStatus,
            staff_user: User | None,
            staff_comment: str | None = None,
            assign_to_staff: User | None = None,
            using_db: BaseDBAsyncClient | None = None,
    ) -> int:
        """
        Update ticket status and set audit fields ('who' and 'when').
        Optionally update staff_comment and staff_assignee.
        """
        values: dict[str, object] = {
            "status": new_status,
            "last_modified_by_id": getattr(staff_user, "id", None),
            "last_modified_at": timezone.now(),
        }
        if staff_comment is not None:
            values["staff_comment"] = staff_comment
        if assign_to_staff is not None:
            values["staff_assignee_id"] = assign_to_staff.id

        return await self.update_by_id(id=ticket_id, values=values, using_db=using_db)

    async def assign_to_self_with_audit(
            self,
            *,
            ticket_id: str,
            staff_user: User,
            using_db: BaseDBAsyncClient | None = None,
    ) -> int:
        """
        Assign the ticket to the given staff member and set audit fields.
        """
        return await self.update_by_id(
            id=ticket_id,
            values={
                "staff_assignee_id": staff_user.id,
                "last_modified_by_id": staff_user.id,
                "last_modified_at": timezone.now(),
            },
            using_db=using_db,
        )
