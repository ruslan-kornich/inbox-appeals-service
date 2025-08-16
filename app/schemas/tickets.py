from datetime import datetime

from pydantic import BaseModel, Field

from app.models import TicketStatus


class CreateTicketBody(BaseModel):
    """User creates a ticket."""

    text: str = Field(min_length=1, max_length=10000)


class TicketListItem(BaseModel):
    """Lightweight listing item to minimize payload."""

    id: str
    status: TicketStatus
    created_at: datetime


class TicketDetail(BaseModel):
    """Detailed ticket view."""

    id: str
    text: str
    status: TicketStatus
    created_at: datetime
    updated_at: datetime
    staff_assignee_id: str | None = None
    staff_comment: str | None = None
    last_modified_by_id: str | None = None
    last_modified_at: datetime | None = None


class StaffUpdateTicketBody(BaseModel):
    """Staff updates status/comment/assignee."""

    status: TicketStatus | None = None
    staff_comment: str | None = None
    assign_to_self: bool | None = None  # convenience flag


class StaffQueueQuery(BaseModel):
    """Optional filters for staff queue."""

    only_my: bool = False
