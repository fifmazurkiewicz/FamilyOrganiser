"""Integration tests for Shopping API router."""

import uuid
import pytest


class TestShoppingListAPI:
    """Tests for /api/v1/shopping/lists endpoints."""

    async def test_create_list(
        self, client, client_auth_headers, family_group
    ):
        response = await client.post(
            "/shopping/lists",
            json={"name": "Groceries", "family_group_id": str(family_group.id)},
            headers=client_auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Groceries"
        assert data["family_group_id"] == str(family_group.id)
        assert "id" in data

    async def test_list_lists(
        self, client, client_auth_headers, family_group
    ):
        await client.post(
            "/shopping/lists",
            json={"name": "List A", "family_group_id": str(family_group.id)},
            headers=client_auth_headers,
        )
        await client.post(
            "/shopping/lists",
            json={"name": "List B", "family_group_id": str(family_group.id)},
            headers=client_auth_headers,
        )

        response = await client.get(
            "/shopping/lists",
            params={"family_group_id": str(family_group.id)},
            headers=client_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_get_list(
        self, client, client_auth_headers, family_group
    ):
        create_resp = await client.post(
            "/shopping/lists",
            json={"name": "To Buy", "family_group_id": str(family_group.id)},
            headers=client_auth_headers,
        )
        list_id = create_resp.json()["id"]

        resp = await client.get(
            f"/shopping/lists/{list_id}",
            headers=client_auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "To Buy"

    async def test_get_list_not_found(
        self, client, client_auth_headers
    ):
        resp = await client.get(
            f"/shopping/lists/{uuid.uuid4()}",
            headers=client_auth_headers,
        )
        assert resp.status_code == 404

    async def test_update_list(
        self, client, client_auth_headers, family_group
    ):
        create_resp = await client.post(
            "/shopping/lists",
            json={"name": "Old Name", "family_group_id": str(family_group.id)},
            headers=client_auth_headers,
        )
        list_id = create_resp.json()["id"]

        resp = await client.patch(
            f"/shopping/lists/{list_id}",
            json={"name": "New Name"},
            headers=client_auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "New Name"

    async def test_delete_list(
        self, client, client_auth_headers, family_group
    ):
        create_resp = await client.post(
            "/shopping/lists",
            json={"name": "Temp", "family_group_id": str(family_group.id)},
            headers=client_auth_headers,
        )
        list_id = create_resp.json()["id"]

        resp = await client.delete(
            f"/shopping/lists/{list_id}",
            headers=client_auth_headers,
        )
        assert resp.status_code == 204

        # Verify gone
        get_resp = await client.get(
            f"/shopping/lists/{list_id}",
            headers=client_auth_headers,
        )
        assert get_resp.status_code == 404


class TestShoppingItemAPI:
    """Tests for /api/v1/shopping/lists/{list_id}/items and /items/{item_id} endpoints."""

    @pytest.fixture
    async def _list(self, client, client_auth_headers, family_group):
        resp = await client.post(
            "/shopping/lists",
            json={"name": "Test List", "family_group_id": str(family_group.id)},
            headers=client_auth_headers,
        )
        return resp.json()["id"]

    async def test_create_item(
        self, client, client_auth_headers, family_group, _list
    ):
        resp = await client.post(
            f"/shopping/lists/{_list}/items",
            json={"name": "Milk", "quantity": 2},
            headers=client_auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Milk"
        assert data["quantity"] == 2
        assert data["is_bought"] is False

    async def test_list_items(
        self, client, client_auth_headers, family_group, _list
    ):
        await client.post(
            f"/shopping/lists/{_list}/items",
            json={"name": "A"}, headers=client_auth_headers,
        )
        await client.post(
            f"/shopping/lists/{_list}/items",
            json={"name": "B"}, headers=client_auth_headers,
        )

        resp = await client.get(
            f"/shopping/lists/{_list}/items",
            headers=client_auth_headers,
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_update_item(
        self, client, client_auth_headers, family_group, _list
    ):
        create_resp = await client.post(
            f"/shopping/lists/{_list}/items",
            json={"name": "Old"}, headers=client_auth_headers,
        )
        item_id = create_resp.json()["id"]

        resp = await client.patch(
            f"/shopping/items/{item_id}",
            json={"name": "New", "quantity": 5},
            headers=client_auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "New"
        assert data["quantity"] == 5

    async def test_toggle_bought(
        self, client, client_auth_headers, family_group, _list
    ):
        create_resp = await client.post(
            f"/shopping/lists/{_list}/items",
            json={"name": "Toggle me"}, headers=client_auth_headers,
        )
        item_id = create_resp.json()["id"]

        # Toggle on
        resp = await client.post(
            f"/shopping/items/{item_id}/toggle",
            headers=client_auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["is_bought"] is True
        assert resp.json()["bought_by"] is not None

        # Toggle off
        resp2 = await client.post(
            f"/shopping/items/{item_id}/toggle",
            headers=client_auth_headers,
        )
        assert resp2.status_code == 200
        assert resp2.json()["is_bought"] is False

    async def test_delete_item(
        self, client, client_auth_headers, family_group, _list
    ):
        create_resp = await client.post(
            f"/shopping/lists/{_list}/items",
            json={"name": "Delete me"}, headers=client_auth_headers,
        )
        item_id = create_resp.json()["id"]

        resp = await client.delete(
            f"/shopping/items/{item_id}",
            headers=client_auth_headers,
        )
        assert resp.status_code == 204

    async def test_unauthorized(self, client):
        """Requests without auth should be rejected."""
        resp = await client.get("/shopping/lists", params={"family_group_id": str(uuid.uuid4())})
        assert resp.status_code == 403