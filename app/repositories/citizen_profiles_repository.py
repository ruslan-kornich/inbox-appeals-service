from tortoise.backends.base.client import BaseDBAsyncClient

from app.models import CitizenProfile

from .base import BaseRepository


class CitizenProfileRepository(BaseRepository[CitizenProfile]):
    """
    Repository for CitizenProfile model.
    """

    def __init__(self) -> None:
        """
        Initialize repository with the CitizenProfile model.
        """
        super().__init__(model=CitizenProfile)

    async def get_by_user_id(
        self,
        user_id: str,
        *,
        using_db: BaseDBAsyncClient | None = None,
    ) -> CitizenProfile | None:
        """Get profile by user id."""
        return await self.get_one(filters={"user_id": user_id}, using_db=using_db)
