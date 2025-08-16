from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.models import UserRole
from app.schemas.tickets import CreateTicketBody, TicketDetail, TicketListItem
from app.security.dependencies import get_current_user, require_roles
from app.services.ticket_service import TicketService

router = APIRouter()
service = TicketService()


@router.post(
    "",
    dependencies=[Depends(require_roles(UserRole.USER))],
    status_code=status.HTTP_201_CREATED,
)
async def create_ticket(
    body: CreateTicketBody,
    current: Annotated[tuple[str, str], Depends(get_current_user)],
) -> TicketDetail:
    """
    Create a ticket for the current USER.
    """
    user_id, _ = current
    ticket = await service.create_ticket(owner_id=user_id, text=body.text)
    return TicketDetail(
        id=str(ticket.id),
        text=ticket.text,
        status=ticket.status,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        staff_assignee_id=str(ticket.staff_assignee_id) if ticket.staff_assignee_id else None,
        staff_comment=ticket.staff_comment,
        last_modified_by_id=str(ticket.last_modified_by_id) if ticket.last_modified_by_id else None,
        last_modified_at=ticket.last_modified_at,
    )


@router.get(
    "/my",
    dependencies=[Depends(require_roles(UserRole.USER))],
)
async def list_my_tickets(
    current: Annotated[tuple[str, str], Depends(get_current_user)],
) -> list[TicketListItem]:
    """
    List tickets of the current USER (lightweight listing).
    """
    user_id, _ = current
    items = await service.list_my_tickets(owner_id=user_id)
    return [TicketListItem(id=str(ticket.id), status=ticket.status, created_at=ticket.created_at) for ticket in items]


@router.get(
    "/my/{ticket_id}",
    dependencies=[Depends(require_roles(UserRole.USER))],
)
async def get_my_ticket(
    ticket_id: str,
    current: Annotated[tuple[str, str], Depends(get_current_user)],
) -> TicketDetail:
    """
    Get a specific ticket of the current USER (detailed).
    """
    user_id, _ = current
    ticket = await service.get_my_ticket(owner_id=user_id, ticket_id=ticket_id)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return TicketDetail(
        id=str(ticket.id),
        text=ticket.text,
        status=ticket.status,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        staff_assignee_id=str(ticket.staff_assignee_id) if ticket.staff_assignee_id else None,
        staff_comment=ticket.staff_comment,
        last_modified_by_id=str(ticket.last_modified_by_id) if ticket.last_modified_by_id else None,
        last_modified_at=ticket.last_modified_at,
    )
