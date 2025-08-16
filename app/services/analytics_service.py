from datetime import datetime, timedelta

from tortoise.functions import Count, Max

from app.models import Ticket, TicketStatus
from app.repositories.tickets_repository import TicketRepository


class AnalyticsService:
    """
    Admin analytics over tickets.
    """

    def __init__(self) -> None:
        self.ticket_repo = TicketRepository()

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

        items = await Ticket.filter(**(filters or {})).annotate(cnt=Count("id")).group_by("status").values("status",
                                                                                                           "cnt")
        by_status: dict[TicketStatus, int] = {TicketStatus(item["status"]): int(item["cnt"]) for item in items}
        # fill missing statuses with 0
        for s in TicketStatus:
            by_status.setdefault(s, 0)

        return total, by_status

    async def staff_performance(
            self,
            *,
            date_from: datetime | None,
            date_to: datetime | None,
    ) -> list[dict]:
        """
        For each staff member who modified tickets in the period, return counts by status
        and last modification timestamp. Uses aggregate query on Ticket.
        """
        filters: dict[str, object] = {"last_modified_by_id__not": None}
        if date_from:
            filters["last_modified_at__gte"] = date_from
        if date_to:
            filters["last_modified_at__lt"] = date_to + timedelta(days=1)

        # Aggregate per staff and status
        rows = await Ticket.filter(**filters).values(
            "last_modified_by_id", "status",
        ).annotate(
            cnt=Count("id"),
            last_mod=Max("last_modified_at"),
        )

        # Reduce to dict[staff_id] = metrics
        perf: dict[str, dict] = {}
        for r in rows:
            staff_id = str(r["last_modified_by_id"])
            status = TicketStatus(r["status"])
            cnt = int(r["cnt"])
            last_mod = r["last_mod"].isoformat() if r["last_mod"] else None

            rec = perf.setdefault(staff_id, {
                "staff_id": staff_id,
                "resolved_count": 0,
                "rejected_count": 0,
                "in_progress_count": 0,
                "last_modified_at_max": None,
            })
            if status == TicketStatus.RESOLVED:
                rec["resolved_count"] += cnt
            elif status == TicketStatus.REJECTED:
                rec["rejected_count"] += cnt
            elif status == TicketStatus.IN_PROGRESS:
                rec["in_progress_count"] += cnt

            # Track max last_mod
            if last_mod and (rec["last_modified_at_max"] is None or last_mod > rec["last_modified_at_max"]):
                rec["last_modified_at_max"] = last_mod

        return list(perf.values())
