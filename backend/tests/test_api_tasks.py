"""Integration tests for Tasks API router."""

import uuid
from datetime import date
import pytest


class TestTaskListAPI:
    async def test_create_list(
        self, client, client_auth_headers, family_group
    ):
        resp = await client.post(
            "/tasks/lists",
            json={"name": "Chores", "family_group_id": str(family_group.id)},
            headers=client_auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Chores"

    async def test_list_lists(
        self, client, client_auth_headers, family_group
    ):
        await client.post(
            "/tasks/lists",
            json={"name": "A", "family_group_id": str(family_group.id)},
            headers=client_auth_headers,
        )
        await client.post(
            "/tasks/lists",
            json={"name": "B", "family_group_id": str(family_group.id)},
            headers=client_auth_headers,
        )
        resp = await client.get(
            "/tasks/lists",
            params={"family_group_id": str(family_group.id)},
            headers=client_auth_headers,
        )
        assert len(resp.json()) == 2

    async def test_get_list(
        self, client, client_auth_headers, family_group
    ):
        create_resp = await client.post(
            "/tasks/lists",
            json={"name": "Errands", "family_group_id": str(family_group.id)},
            headers=client_auth_headers,
        )
        list_id = create_resp.json()["id"]
        resp = await client.get(f"/tasks/lists/{list_id}", headers=client_auth_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Errands"

    async def test_update_list(
        self, client, client_auth_headers, family_group
    ):
        create_resp = await client.post(
            "/tasks/lists",
            json={"name": "Old", "family_group_id": str(family_group.id)},
            headers=client_auth_headers,
        )
        list_id = create_resp.json()["id"]
        resp = await client.patch(
            f"/tasks/lists/{list_id}",
            json={"name": "Renamed"},
            headers=client_auth_headers,
        )
        assert resp.json()["name"] == "Renamed"

    async def test_delete_list(
        self, client, client_auth_headers, family_group
    ):
        create_resp = await client.post(
            "/tasks/lists",
            json={"name": "Temp", "family_group_id": str(family_group.id)},
            headers=client_auth_headers,
        )
        list_id = create_resp.json()["id"]
        resp = await client.delete(
            f"/tasks/lists/{list_id}", headers=client_auth_headers
        )
        assert resp.status_code == 204


class TestTaskItemAPI:
    @pytest.fixture
    async def _list(self, client, client_auth_headers, family_group):
        resp = await client.post(
            "/tasks/lists",
            json={"name": "Test", "family_group_id": str(family_group.id)},
            headers=client_auth_headers,
        )
        return resp.json()["id"]

    async def test_create_item(
        self, client, client_auth_headers, family_group, _list
    ):
        resp = await client.post(
            f"/tasks/lists/{_list}/items",
            json={"title": "Clean room", "due_date": "2026-08-01"},
            headers=client_auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Clean room"
        assert data["is_done"] is False
        assert data["due_date"] == "2026-08-01"

    async def test_list_items(
        self, client, client_auth_headers, family_group, _list
    ):
        await client.post(
            f"/tasks/lists/{_list}/items",
            json={"title": "Task 1"}, headers=client_auth_headers,
        )
        await client.post(
            f"/tasks/lists/{_list}/items",
            json={"title": "Task 2"}, headers=client_auth_headers,
        )
        resp = await client.get(
            f"/tasks/lists/{_list}/items", headers=client_auth_headers
        )
        assert len(resp.json()) == 2

    async def test_update_item(
        self, client, client_auth_headers, family_group, _list
    ):
        create_resp = await client.post(
            f"/tasks/lists/{_list}/items",
            json={"title": "Old"}, headers=client_auth_headers,
        )
        item_id = create_resp.json()["id"]
        resp = await client.patch(
            f"/tasks/items/{item_id}",
            json={"title": "New Title"},
            headers=client_auth_headers,
        )
        assert resp.json()["title"] == "New Title"

    async def test_toggle_done(
        self, client, client_auth_headers, family_group, _list
    ):
        create_resp = await client.post(
            f"/tasks/lists/{_list}/items",
            json={"title": "Toggle"}, headers=client_auth_headers,
        )
        item_id = create_resp.json()["id"]

        resp = await client.post(
            f"/tasks/items/{item_id}/toggle",
            headers=client_auth_headers,
        )
        assert resp.json()["is_done"] is True
        assert resp.json()["done_by"] is not None

        resp2 = await client.post(
            f"/tasks/items/{item_id}/toggle",
            headers=client_auth_headers,
        )
        assert resp2.json()["is_done"] is False

    async def test_delete_item(
        self, client, client_auth_headers, family_group, _list
    ):
        create_resp = await client.post(
            f"/tasks/lists/{_list}/items",
            json={"title": "Delete me"}, headers=client_auth_headers,
        )
        item_id = create_resp.json()["id"]
        resp = await client.delete(
            f"/tasks/items/{item_id}", headers=client_auth_headers
        )
        assert resp.status_code == 204

    @pytest.mark.skip(reason="Dependency override always sets valid user")
    async def test_unauthorized(self, client):
        resp = await client.get("/tasks/lists", params={"family_group_id": str(uuid.uuid4())})
        assert resp.status_code == 403