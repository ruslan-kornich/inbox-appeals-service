from fastapi import APIRouter, Depends, HTTPException, status

from app.models import TicketStatus, UserRole
from app.repositories.users_repository import UserRepository
from app.schemas.tickets import StaffUpdateTicketBody, TicketDetail, TicketListItem
from app.security.dependencies import get_current_user, require_roles
from app.services.staff_service import StaffService

router = APIRouter()
service = StaffService()
user_repo = UserRepository()


@router.get("", response_model=list[TicketListItem], dependencies=[Depends(require_roles(UserRole.STAFF))])
async def list_queue(only_my: bool = False, current=Depends(get_current_user)):
    """
    Staff queue listing: NEW/IN_PROGRESS by default; if only_my=True — only assigned to self.
    """
    user_id, _ = current
    staff_user = await user_repo.get_by_id(id=user_id)
    items = await service.list_queue(staff_user=staff_user, only_my=only_my)
    return [TicketListItem(id=str(t.id), status=t.status, created_at=t.created_at) for t in items]


@router.get("/{ticket_id}", response_model=TicketDetail, dependencies=[Depends(require_roles(UserRole.STAFF))])
async def get_ticket(ticket_id: str):
    """
    Detailed view for staff.
    """
    ticket = await service.get_ticket(ticket_id=ticket_id)
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


@router.patch("/{ticket_id}", dependencies=[Depends(require_roles(UserRole.STAFF))],
              status_code=status.HTTP_204_NO_CONTENT)
async def update_ticket(ticket_id: str, body: StaffUpdateTicketBody, current=Depends(get_current_user)):
    """
    Update status/comment; optionally assign to self (assign_to_self=True).
    """
    user_id, _ = current
    staff_user = await user_repo.get_by_id(id=user_id)
    new_status = body.status or TicketStatus.IN_PROGRESS
    affected = await service.update_ticket(
        ticket_id=ticket_id,
        staff_user=staff_user,
        new_status=new_status,
        staff_comment=body.staff_comment,
        assign_to_self=bool(body.assign_to_self),
    )
    if affected == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nothing changed")
