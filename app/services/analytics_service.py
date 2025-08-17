from datetime import datetime, timedelta
from uuid import UUID

from tortoise.functions import Count, Max

from app.models import Ticket, TicketStatus, UserRole
from app.repositories.tickets_repository import TicketRepository
from app.repositories.users_repository import UserRepository


class AnalyticsService:
    """
    Admin analytics over tickets.
    """

    def __init__(self) -> None:
        """
        Initialize AnalyticsService with a TicketRepository instance.
        """
        self.ticket_repo = TicketRepository()
        self.user_repo = UserRepository()

    async def overview(
        self,
        *,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> tuple[int, dict[TicketStatus, int]]:
        """
        Return total created count and counts by status in the given period.
        """
        filters: dict[str, object] = {}
        if date_from:
            filters["created_at__gte"] = date_from
        if date_to:
            # inclusive end-of-day
            filters["created_at__lt"] = date_to + timedelta(days=1)

        total = await self.ticket_repo.count(filters=filters or None)

        items = (
            await Ticket.filter(**(filters or {}))
            .annotate(cnt=Count("id"))
            .group_by("status")
            .values("status", "cnt")
        )
        by_status: dict[TicketStatus, int] = {TicketStatus(item["status"]): int(item["cnt"]) for item in items}
        # fill missing statuses with 0
        for status in TicketStatus:
            by_status.setdefault(status, 0)

        return total, by_status

    async def staff_performance(
        self,
        *,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        staff_id: UUID | None = None,
    ) -> list[dict]:
        filters: dict[str, object] = {}

        if staff_id:
            filters["last_modified_by_id"] = str(staff_id)
        else:
            filters["last_modified_by_id__not"] = None

        if date_from:
            filters["last_modified_at__gte"] = date_from
        if date_to:
            filters["last_modified_at__lt"] = date_to + timedelta(days=1)
        rows = (
            await Ticket.filter(**filters)
            .annotate(cnt=Count("id"), last_mod=Max("last_modified_at"))
            .group_by("last_modified_by_id", "status")
            .values("last_modified_by_id", "status", "cnt", "last_mod")
        )

        performance_map: dict[str, dict] = {}

        for row in rows:
            staff_id_str = str(row["last_modified_by_id"])
            status = TicketStatus(row["status"])
            count = int(row["cnt"])
            last_modified = row["last_mod"].isoformat() if row["last_mod"] else None

            record = performance_map.setdefault(
                staff_id_str,
                {
                    "staff_id": staff_id_str,
                    "resolved_count": 0,
                    "rejected_count": 0,
                    "in_progress_count": 0,
                    "last_modified_at_max": None,
                },
            )

            if status == TicketStatus.RESOLVED:
                record["resolved_count"] += count
            elif status == TicketStatus.REJECTED:
                record["rejected_count"] += count
            elif status == TicketStatus.IN_PROGRESS:
                record["in_progress_count"] += count

            if last_modified and (
                record["last_modified_at_max"] is None or last_modified > record["last_modified_at_max"]
            ):
                record["last_modified_at_max"] = last_modified
        all_staff = await self.user_repo.list_records(filters={"role": UserRole.STAFF})
        for staff in all_staff:
            staff_id_str = str(staff.id)
            if staff_id_str not in performance_map:
                performance_map[staff_id_str] = {
                    "staff_id": staff_id_str,
                    "resolved_count": 0,
                    "rejected_count": 0,
                    "in_progress_count": 0,
                    "last_modified_at_max": None,
                }

        return list(performance_map.values())
