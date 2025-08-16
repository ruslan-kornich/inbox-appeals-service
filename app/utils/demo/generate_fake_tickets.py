import asyncio
import random

from faker import Faker
from tortoise import timezone

from app.config.db import DatabaseManager
from app.models import TicketStatus, UserRole
from app.repositories.tickets_repository import TicketRepository
from app.repositories.users_repository import UserRepository

faker = Faker("uk_UA")


async def generate_fake_tickets():
    await DatabaseManager.setup()

    user_repo = UserRepository()
    ticket_repo = TicketRepository()

    # Получаем пользователей по ролям
    user_owners = await user_repo.list_records(filters={"role": UserRole.USER})
    staff_users = await user_repo.list_records(filters={"role": UserRole.STAFF})

    if not user_owners or not staff_users:
        print("❌ Not enough users to generate tickets.")
        await DatabaseManager.stop()
        return

    tickets_to_create = []

    def generate_ticket(status: TicketStatus):
        owner = random.choice(user_owners)
        ticket = {
            "owner_id": owner.id,
            "text": faker.paragraph(nb_sentences=3),
            "status": status,
        }

        if status in {TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED, TicketStatus.REJECTED}:
            staff = random.choice(staff_users)
            ticket["staff_assignee_id"] = staff.id
            ticket["staff_comment"] = faker.sentence()
            ticket["last_modified_by_id"] = staff.id
            ticket["last_modified_at"] = timezone.now()

        return ticket

    # Генерация тикетов по статусам
    tickets_to_create += [generate_ticket(TicketStatus.NEW) for _ in range(300)]
    tickets_to_create += [generate_ticket(TicketStatus.IN_PROGRESS) for _ in range(100)]
    tickets_to_create += [generate_ticket(TicketStatus.RESOLVED) for _ in range(100)]
    tickets_to_create += [generate_ticket(TicketStatus.REJECTED) for _ in range(50)]

    await ticket_repo.bulk_create(values=tickets_to_create)

    print(f"✅ Created {len(tickets_to_create)} fake tickets.")

    await DatabaseManager.stop()


if __name__ == "__main__":
    try:
        # python3 -m app.utils.demo.generate_fake_tickets
        asyncio.run(generate_fake_tickets())
    except KeyboardInterrupt:
        print("\nInterrupted.")
