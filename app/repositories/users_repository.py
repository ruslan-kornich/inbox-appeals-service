from fastapi_pagination import Page
from tortoise.backends.base.client import BaseDBAsyncClient

from app.models import User, UserRole

from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Repository for User model with common lookups.
    """

    def __init__(self) -> None:
        """
        Initialize repository with the User model.
        """
        super().__init__(model=User)

    async def get_by_email(self, email: str, *, using_db: BaseDBAsyncClient | None = None) -> User | None:
        """Retrieve user by unique email."""
        return await self.get_one(filters={"email": email}, using_db=using_db)

    async def list_staff(self, *, using_db: BaseDBAsyncClient | None = None) -> list[User]:
        """List all staff members."""
        return await self.list_records(filters={"role": UserRole.STAFF}, using_db=using_db)

    async def list_admins(self, *, using_db: BaseDBAsyncClient | None = None) -> list[User]:
        """List all admins."""
        return await self.list_records(filters={"role": UserRole.ADMIN}, using_db=using_db)

    async def paginate_users(self, *, using_db: BaseDBAsyncClient | None = None) -> Page[User]:
        """Paginated list of regular users (role=USER)."""
        return await self.paginate(filters={"role": UserRole.USER}, using_db=using_db)

    async def list_users_paginated(
        self,
        *,
        page: int,
        size: int,
        using_db: BaseDBAsyncClient | None = None,
    ) -> tuple[list[User], int]:
        """
        Return paginated list of users with role=USER and total count.
        """
        filters = {"role": UserRole.USER}
        offset = (page - 1) * size

        records = await self.list_records(
            filters=filters,
            offset=offset,
            limit=size,
            order_by=["created_at"],  # or email if preferred
            using_db=using_db,
        )

        total = await self.count(filters=filters, using_db=using_db)
        return records, total

    async def promote_to_staff(self, user_id: str, *, using_db: BaseDBAsyncClient | None = None) -> int:
        """Promote a user to STAFF role."""
        return await self.update_by_id(pk=user_id, values={"role": UserRole.STAFF}, using_db=using_db)
