from app.models import User, UserRole
from app.repositories.users_repository import UserRepository
from app.services.auth_service import hash_password


class AdminService:
    """
    Admin operations: manage staff and user accounts.
    """

    def __init__(self) -> None:
        """
        Initialize AdminService with a UserRepository instance.
        """
        self.user_repo = UserRepository()

    async def list_staff(self) -> list[User]:
        """
        Return all staff users.
        """
        return await self.user_repo.list_staff()

    async def create_staff(self, *, email: str, password: str) -> User:
        """
        Create a new STAFF user.

        Raises:
            ValueError: If the email is already registered.

        """
        if await self.user_repo.exists(filters={"email": email}):
            error_message = "Email already registered"
            raise ValueError(error_message)

        async with self.user_repo.transaction() as conn:
            return await self.user_repo.create(
                values={
                    "email": email,
                    "password_hash": hash_password(password),
                    "role": UserRole.STAFF,
                },
                using_db=conn,
            )

    async def list_users_paginated(self, *, page: int, size: int) -> tuple[list[User], int]:
        """
        Return paginated list of users (role=USER) with total count.

        :param page: Page number (1-based).
        :param size: Page size.
        :return: Tuple of (users, total_count).
        """
        return await self.user_repo.list_users_paginated(page=page, size=size)
