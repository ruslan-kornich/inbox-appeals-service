from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends

from app.models import UserRole
from app.schemas.analytics import OverviewStats, StaffPerformanceItem, StaffPerformanceResponse
from app.security.dependencies import require_roles
from app.services.analytics_service import AnalyticsService

router = APIRouter()
service = AnalyticsService()


@router.get(
    "/overview",
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def analytics_overview(date_from: str | None = None, date_to: str | None = None) -> OverviewStats:
    """
    Overview counts for created tickets and per-status distribution.
    """
    parsed_date_from = datetime.fromisoformat(date_from) if date_from else None
    parsed_date_to = datetime.fromisoformat(date_to) if date_to else None
    total_created, by_status = await service.overview(date_from=parsed_date_from, date_to=parsed_date_to)
    return OverviewStats(total_created=total_created, by_status=by_status)


@router.get(
    "/staff-performance",
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def analytics_staff_performance(
        date_from: str | None = None,
        date_to: str | None = None,
        staff_id: UUID | None = None,
) -> StaffPerformanceResponse:
    """
    Per-staff metrics (resolved/rejected/in_progress + last modification).

    Optional filter: staff_id.
    """
    parsed_date_from = datetime.fromisoformat(date_from) if date_from else None
    parsed_date_to = datetime.fromisoformat(date_to) if date_to else None
    items_raw = await service.staff_performance(
        date_from=parsed_date_from,
        date_to=parsed_date_to,
        staff_id=staff_id,
    )
    items = [StaffPerformanceItem(**item) for item in items_raw]
    return StaffPerformanceResponse(items=items)
