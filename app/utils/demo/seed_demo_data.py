import asyncio
import random
import sys

from faker import Faker
from tortoise import timezone

from app.config.db import DatabaseManager
from app.models import Ticket, User, TicketStatus, UserRole
from app.repositories.users_repository import UserRepository
from app.repositories.tickets_repository import TicketRepository
from app.services.auth_service import hash_password

faker = Faker("uk_UA")

ADMIN_EMAIL = "admin@i.ua"
DEMO_PASSWORD = "Strong123!"


async def reset_database():
    """
    Clears all Ticket and User data except the admin user.
    """
    print("🧹 Resetting database...")
    await Ticket.all().delete()
    await User.exclude(email=ADMIN_EMAIL).delete()
    print("✅ Database reset complete.")


async def seed_demo_data(reset: bool = False):
    await DatabaseManager.setup()

    if reset:
        await reset_database()

    user_repo = UserRepository()
    ticket_repo = TicketRepository()

    # 1. Ensure Admin exists
    admin = await user_repo.get_by_email(ADMIN_EMAIL)
    if not admin:
        print("👤 Creating admin user...")
        admin = await user_repo.create(values={
            "email": ADMIN_EMAIL,
            "password_hash": hash_password(DEMO_PASSWORD),
            "role": UserRole.ADMIN
        })
        print(f"✅ Admin created: {ADMIN_EMAIL}")
    else:
        print(f"⚠️  Admin already exists: {ADMIN_EMAIL}")

    # 2. Create 10 STAFF users
    print("👥 Creating 10 staff users...")
    for i in range(10):
        await user_repo.create(values={
            "email": f"staff{i+1}@example.com",
            "password_hash": hash_password(DEMO_PASSWORD),
            "role": UserRole.STAFF,
        })
    print("✅ 10 staff users created.")

    # 3. Create 30 USER users
    print("👤 Creating 30 user accounts...")
    for i in range(30):
        await user_repo.create(values={
            "email": f"user{i+1}@example.com",
            "password_hash": hash_password(DEMO_PASSWORD),
            "role": UserRole.USER,
        })
    print("✅ 30 users created.")

    # 4. Generate 300 tickets (10 per user)
    print("🧾 Generating fake tickets...")

    user_owners = await user_repo.list_records(filters={"role": UserRole.USER})
    staff_users = await user_repo.list_records(filters={"role": UserRole.STAFF})

    tickets_to_create = []

    for user in user_owners:
        for _ in range(10):
            status = random.choices(
                population=[
                    TicketStatus.NEW,
                    TicketStatus.IN_PROGRESS,
                    TicketStatus.RESOLVED,
                    TicketStatus.REJECTED,
                ],
                weights=[0.5, 0.2, 0.2, 0.1],
                k=1
            )[0]

            ticket = {
                "owner_id": user.id,
                "text": faker.paragraph(nb_sentences=3),
                "status": status,
            }

            if status != TicketStatus.NEW:
                staff = random.choice(staff_users)
                ticket.update({
                    "staff_assignee_id": staff.id,
                    "staff_comment": faker.sentence(),
                    "last_modified_by_id": staff.id,
                    "last_modified_at": timezone.now(),
                })

            tickets_to_create.append(ticket)

    await ticket_repo.bulk_create(values=tickets_to_create)
    print(f"✅ Created {len(tickets_to_create)} fake tickets.")

    await DatabaseManager.stop()


if __name__ == "__main__":
    try:
        # Run with: python3 -m app.utils.demo.seed_demo_data --reset
        reset_flag = "--reset" in sys.argv
        asyncio.run(seed_demo_data(reset=reset_flag))
    except KeyboardInterrupt:
        print("\nInterrupted.")
