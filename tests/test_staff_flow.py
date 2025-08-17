"""
Staff flow tests:
- STAFF sees NEW tickets in the queue.
- STAFF assigns ticket to self and moves it to IN_PROGRESS.
- STAFF resolves the ticket with a comment and audit fields are updated.
"""

import pytest

from app.models import TicketStatus
from .conftest import auth_header


@pytest.mark.asyncio
async def test_staff_queue_and_updates(client, register_user_factory, make_staff_factory):
    # Setup: one USER and one STAFF
    user_id, user_token = await register_user_factory("owner@example.com", "Strong123!")
    staff_id, staff_token = await make_staff_factory("staff1@example.com", "Strong123!")

    # User creates a NEW ticket
    create_response = await client.post(
        "/tickets",
        json={"text": "Please help me"},
        headers=auth_header(user_token),
    )
    assert create_response.status_code == 201
    ticket_id = create_response.json()["id"]

    # STAFF lists queue (should include the ticket)
    queue_response = await client.get("/staff/tickets", headers=auth_header(staff_token))
    assert queue_response.status_code == 200
    queue = queue_response.json()
    assert any(item["id"] == ticket_id for item in queue)

    # STAFF assigns to self and updates status to IN_PROGRESS
    patch_response = await client.patch(
        f"/staff/tickets/{ticket_id}",
        json={
            "assign_to_self": True,
            "status": "IN_PROGRESS",
            "staff_comment": "Working on it",
        },
        headers=auth_header(staff_token),
    )
    assert patch_response.status_code == 204

    # Verify the ticket is updated correctly
    detail_response = await client.get(f"/staff/tickets/{ticket_id}", headers=auth_header(staff_token))
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["status"] == TicketStatus.IN_PROGRESS.value
    assert detail["staff_assignee_id"] == staff_id
    assert detail["staff_comment"] == "Working on it"
    assert detail["last_modified_by_id"] == staff_id
    assert detail["last_modified_at"] is not None

    # STAFF lists only their assigned tickets — should include the ticket
    only_my_response = await client.get("/staff/tickets?only_my=true", headers=auth_header(staff_token))
    assert only_my_response.status_code == 200
    only_my_queue = only_my_response.json()
    assert any(item["id"] == ticket_id for item in only_my_queue)

    # STAFF resolves the ticket
    resolve_response = await client.patch(
        f"/staff/tickets/{ticket_id}",
        json={
            "status": "RESOLVED",
            "staff_comment": "Issue fixed",
        },
        headers=auth_header(staff_token),
    )
    assert resolve_response.status_code == 204

    # Verify final RESOLVED state
    final_response = await client.get(f"/staff/tickets/{ticket_id}", headers=auth_header(staff_token))
    assert final_response.status_code == 200
    final_detail = final_response.json()
    assert final_detail["status"] == TicketStatus.RESOLVED.value
    assert final_detail["staff_comment"] == "Issue fixed"
