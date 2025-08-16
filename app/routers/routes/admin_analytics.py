# app/routes/admin_analytics.py
from datetime import datetime

from fastapi import APIRouter, Depends

from app.models import UserRole
from app.schemas.analytics import OverviewStats, StaffPerformanceItem, StaffPerformanceResponse
from app.security.dependencies import require_roles
from app.services.analytics_service import AnalyticsService

router = APIRouter()
service = AnalyticsService()


@router.get("/overview", response_model=OverviewStats, dependencies=[Depends(require_roles(UserRole.ADMIN))])
async def analytics_overview(date_from: str | None = None, date_to: str | None = None):
    """
    Overview counts for created tickets and per-status distribution.
    """
    df = datetime.fromisoformat(date_from) if date_from else None
    dt = datetime.fromisoformat(date_to) if date_to else None
    total, by_status = await service.overview(date_from=df, date_to=dt)
    return OverviewStats(total_created=total, by_status=by_status)


from uuid import UUID


@router.get("/staff-performance", response_model=StaffPerformanceResponse, dependencies=[Depends(require_roles(UserRole.ADMIN))])
async def analytics_staff_performance(
    date_from: str | None = None,
    date_to: str | None = None,
    staff_id: UUID | None = None,
):
    """
    Per-staff metrics (resolved/rejected/in_progress + last modification).
    Optional filter: staff_id
    """
    df = datetime.fromisoformat(date_from) if date_from else None
    dt = datetime.fromisoformat(date_to) if date_to else None
    items_raw = await service.staff_performance(date_from=df, date_to=dt, staff_id=staff_id)
    items = [StaffPerformanceItem(**itm) for itm in items_raw]
    return StaffPerformanceResponse(items=items)
