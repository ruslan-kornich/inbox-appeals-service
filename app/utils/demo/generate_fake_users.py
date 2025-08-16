import asyncio
from typing import Literal
from random import randint

from faker import Faker

from app.config.db import DatabaseManager
from app.models import UserRole
from app.repositories.users_repository import UserRepository
from app.repositories.citizen_profiles_repository import CitizenProfileRepository
from app.services.auth_service import hash_password

faker = Faker("uk_UA")  # Генерирует украинские ФИО и номера
PASSWORD = "Strong123!"
PASSWORD_HASH = hash_password(PASSWORD)


async def generate_staff_users(count: int):
    repo = UserRepository()
    users_data = [
        {
            "email": faker.unique.email(),
            "password_hash": PASSWORD_HASH,
            "role": UserRole.STAFF,
        }
        for _ in range(count)
    ]
    created = await repo.bulk_create(values=users_data)
    print(f"✅ Created {len(created)} STAFF users")


async def generate_user_with_profiles(count: int):
    user_repo = UserRepository()
    profile_repo = CitizenProfileRepository()

    users_data = []
    profiles_data = []

    for _ in range(count):
        email = faker.unique.email()
        users_data.append({
            "email": email,
            "password_hash": PASSWORD_HASH,
            "role": UserRole.USER,
        })

    users = await user_repo.bulk_create(values=users_data)

    for user in users:
        profiles_data.append({
            "user_id": user.id,
            "inn": faker.unique.bothify(text="##########"),  # 10-значный ИНН
            "phone": faker.unique.phone_number(),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "middle_name": faker.first_name(),
            "birth_date": faker.date_of_birth(minimum_age=18, maximum_age=65),
        })

    await profile_repo.bulk_create(values=profiles_data)

    print(f"✅ Created {len(users)} USER users with profiles")


async def main():
    await DatabaseManager.setup()

    await generate_staff_users(10)
    await generate_user_with_profiles(20)

    await DatabaseManager.stop()


if __name__ == "__main__":
    # python3 -m app.utils.demo.generate_fake_users
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted.")

