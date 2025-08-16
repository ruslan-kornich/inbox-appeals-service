from datetime import date

from pydantic import BaseModel

from app.models import TicketStatus


class DateRangeQuery(BaseModel):
    """Date range filter."""

    date_from: date | None = None
    date_to: date | None = None


class OverviewStats(BaseModel):
    """Admin overview: counts by status and totals."""

    total_created: int
    by_status: dict[TicketStatus, int]


class StaffPerformanceItem(BaseModel):
    """Per-staff effectiveness."""

    staff_id: str
    resolved_count: int
    rejected_count: int
    in_progress_count: int
    last_modified_at_max: str | None = None


class StaffPerformanceResponse(BaseModel):
    items: list[StaffPerformanceItem]
