


from app.models import User, UserRole
from app.repositories.users_repository import UserRepository
from app.services.auth_service import hash_password


class AdminService:
    """
    Admin operations: manage staff users.
    """

    def __init__(self) -> None:
        self.user_repo = UserRepository()

    async def list_staff(self) -> list[User]:
        """Return all staff users."""
        return await self.user_repo.list_staff()

    async def create_staff(self, *, email: str, password: str) -> User:
        """
        Create a new STAFF user.
        """
        if await self.user_repo.exists(filters={"email": email}):
            raise ValueError("Email already registered")
        async with self.user_repo.transaction() as conn:
            user = await self.user_repo.create(
                values={
                    "email": email,
                    "password_hash": hash_password(password),
                    "role": UserRole.STAFF,
                },
                using_db=conn,
            )
        return user

    async def list_users_paginated(self, *, page: int, size: int) -> tuple[list[User], int]:
        return await self.user_repo.list_users_paginated(page=page, size=size)
