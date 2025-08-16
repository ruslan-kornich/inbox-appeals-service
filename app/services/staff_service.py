from app.models import Ticket, TicketStatus, User
from app.repositories.tickets_repository import TicketRepository


class StaffService:
    """
    Staff-facing ticket processing operations.
    """

    def __init__(self) -> None:
        """
        Initialize StaffService with a TicketRepository instance.
        """
        self.ticket_repo = TicketRepository()

    async def list_queue(
            self,
            *,
            staff_user: User,
            only_my: bool = False,
            statuses: list[TicketStatus] | None = None,
    ) -> list[Ticket]:
        """
        List tickets for processing. If only_my=True, return tickets assigned to staff_user.
        """
        return await self.ticket_repo.list_for_staff_queue(
            statuses=statuses or [TicketStatus.NEW, TicketStatus.IN_PROGRESS],
            assignee_id=(str(staff_user.id) if only_my else None),
        )

    async def get_ticket(self, *, ticket_id: str) -> Ticket | None:
        """
        Detailed ticket for staff.
        """
        return await self.ticket_repo.get_by_id(
            id=ticket_id,
            select_related=["owner", "staff_assignee", "last_modified_by"],
        )

    async def update_ticket(
            self,
            *,
            ticket_id: str,
            staff_user: User | None,
            new_status: TicketStatus | None = None,
            staff_comment: str | None = None,
            assign_to_self: bool | None = None,
    ) -> int:
        """
        Update ticket with audit fields; optionally assign to current staff.
        """
        assign_target = staff_user if assign_to_self else None
        if new_status is None and staff_comment is None and assign_target is None:
            return 0
        return await self.ticket_repo.update_status_with_audit(
            ticket_id=ticket_id,
            new_status=new_status or TicketStatus.IN_PROGRESS,
            staff_user=staff_user,
            staff_comment=staff_comment,
            assign_to_staff=assign_target,
        )
