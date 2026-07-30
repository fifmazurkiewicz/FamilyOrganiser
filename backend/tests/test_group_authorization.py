"""Cross-group authorization tests (IDOR protection)."""

import uuid

import pytest


@pytest.mark.asyncio
async def test_shopping_list_forbidden_for_non_member(
    client, client_auth_headers, family_group2, test_user
):
    """User who is not a member cannot list shopping lists for another group."""
    resp = await client.get(
        "/shopping/lists",
        params={"family_group_id": str(family_group2.id)},
        headers=client_auth_headers,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_shopping_list_access_by_id_forbidden(
    db_session, client, client_auth_headers, family_group2, test_user
):
    """User cannot fetch a shopping list belonging to a group they don't belong to."""
    from app.models.shopping import ShoppingList

    foreign_list = ShoppingList(
        name="Foreign",
        family_group_id=family_group2.id,
        created_by=test_user.id,
    )
    db_session.add(foreign_list)
    await db_session.flush()
    await db_session.refresh(foreign_list)

    resp = await client.get(
        f"/shopping/lists/{foreign_list.id}",
        headers=client_auth_headers,
    )
    assert resp.status_code == 403
