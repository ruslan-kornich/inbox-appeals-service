

import asyncio
import sys

from getpass import getpass

from app.config.db import DatabaseManager
from app.models import UserRole
from app.repositories.users_repository import UserRepository
from app.services.auth_service import hash_password


async def create_admin_user():
    """
    CLI utility to create an ADMIN user with a hashed password.
    """

    print("👤 Create admin user\n")

    email = input("Email: ").strip()
    password = getpass("Password (input hidden): ").strip()
    confirm_password = getpass("Confirm Password: ").strip()

    if password != confirm_password:
        print("❌ Passwords do not match.")
        sys.exit(1)

    await DatabaseManager.setup()

    repo = UserRepository()
    if await repo.exists(filters={"email": email}):
        print("⚠️  User with this email already exists.")
        await DatabaseManager.stop()
        sys.exit(1)

    hashed_password = hash_password(password)

    async with repo.transaction() as db:
        user = await repo.create(
            values={
                "email": email,
                "password_hash": hashed_password,
                "role": UserRole.ADMIN,
            },
            using_db=db,
        )
        print(f"✅ Admin user created: {user.email} (id={user.id})")

    await DatabaseManager.stop()


if __name__ == "__main__":
    try:
        #python3 -m app.utils.demo.create_admin
        asyncio.run(create_admin_user())
    except KeyboardInterrupt:
        print("\nInterrupted.")
