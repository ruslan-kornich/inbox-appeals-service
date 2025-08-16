
from app.models import Ticket, TicketStatus
from app.repositories.tickets_repository import TicketRepository


class TicketService:
    """
    User-facing ticket actions.
    """

    def __init__(self) -> None:
        self.ticket_repo = TicketRepository()

    async def create_ticket(self, *, owner_id: str, text: str) -> Ticket:
        """
        Create a new ticket for the given owner.
        """
        async with self.ticket_repo.transaction() as conn:
            ticket = await self.ticket_repo.create(
                values={
                    "owner_id": owner_id,
                    "text": text,
                    "status": TicketStatus.NEW,
                },
                using_db=conn,
            )
        return ticket

    async def list_my_tickets(self, *, owner_id: str) -> list[Ticket]:
        """
        List tickets owned by a user.
        """
        return await self.ticket_repo.list_by_owner(owner_id=owner_id)

    async def get_my_ticket(self, *, owner_id: str, ticket_id: str) -> Ticket | None:
        """
        Retrieve a single ticket if it belongs to the owner.
        """
        ticket = await self.ticket_repo.get_by_id(
            id=ticket_id,
            select_related=["staff_assignee", "last_modified_by"],
        )
        if ticket is None or str(ticket.owner_id) != owner_id:
            return None
        return ticket
