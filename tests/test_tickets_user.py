"""
User tickets API tests:
- Create a ticket as USER.
- List own tickets.
- Get own ticket by id.
- Access to another user's ticket is denied (404).
"""

import pytest

from .conftest import auth_header


@pytest.mark.asyncio
async def test_user_ticket_crud_flow(client, register_user_factory):
    # Register user and login (token minted by fixture)
    user_id, access_token = await register_user_factory("ticketuser@example.com", "Strong123!")

    # Create a ticket
    create_body = {"text": "My first request"}
    response = await client.post("/tickets", json=create_body, headers=auth_header(access_token))
    assert response.status_code == 201
    ticket = response.json()
    assert ticket["text"] == "My first request"
    ticket_id = ticket["id"]

    # List "my" tickets
    response = await client.get("/tickets/my", headers=auth_header(access_token))
    assert response.status_code == 200
    items = response.json()
    assert any(item["id"] == ticket_id for item in items)

    # Get "my" ticket by id
    response = await client.get(f"/tickets/my/{ticket_id}", headers=auth_header(access_token))
    assert response.status_code == 200
    detail = response.json()
    assert detail["id"] == ticket_id
    assert detail["status"] == "NEW"

    # Another user should NOT see this ticket
    other_user_id, other_token = await register_user_factory("otheruser@example.com", "Strong123!")
    response = await client.get(f"/tickets/my/{ticket_id}", headers=auth_header(other_token))
    assert response.status_code == 404
