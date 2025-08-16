from app.models import User, UserRole
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Repository for User model with common lookups.
    """

    def __init__(self) -> None:
        super().__init__(model=User)

    async def get_by_email(self, email: str, *, using_db=None) -> User | None:
        """Retrieve user by unique email."""
        return await self.get_one(filters={"email": email}, using_db=using_db)

    async def list_staff(self, *, using_db=None) -> list[User]:
        """List all staff members."""
        return await self.list_records(filters={"role": UserRole.STAFF}, using_db=using_db)

    async def list_admins(self, *, using_db=None) -> list[User]:
        """List all admins."""
        return await self.list_records(filters={"role": UserRole.ADMIN}, using_db=using_db)

    async def promote_to_staff(self, user_id: str, *, using_db=None) -> int:
        """Promote a user to STAFF role."""
        return await self.update_by_id(id=user_id, values={"role": UserRole.STAFF}, using_db=using_db)
