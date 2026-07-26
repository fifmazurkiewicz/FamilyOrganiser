"""Integration tests for Simple Expenses API router."""

import uuid
from datetime import date
import pytest


class TestSimpleExpenseAPI:
    async def test_create_expense(
        self, client, client_auth_headers, family_group
    ):
        resp = await client.post(
            "/simple-expenses/",
            json={
                "family_group_id": str(family_group.id),
                "amount": "42.50",
                "description": "Groceries",
                "expense_date": "2026-07-20",
            },
            headers=client_auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["description"] == "Groceries"
        assert data["amount"] == "42.50"
        assert data["expense_date"] == "2026-07-20"
        assert "id" in data

    async def test_list_expenses(
        self, client, client_auth_headers, family_group
    ):
        await client.post(
            "/simple-expenses/",
            json={
                "family_group_id": str(family_group.id),
                "amount": "10",
                "description": "July expense",
                "expense_date": "2026-07-01",
            },
            headers=client_auth_headers,
        )
        await client.post(
            "/simple-expenses/",
            json={
                "family_group_id": str(family_group.id),
                "amount": "20",
                "description": "August expense",
                "expense_date": "2026-08-01",
            },
            headers=client_auth_headers,
        )

        resp = await client.get(
            "/simple-expenses/",
            params={"family_group_id": str(family_group.id)},
            headers=client_auth_headers,
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_list_expenses_date_filter(
        self, client, client_auth_headers, family_group
    ):
        await client.post(
            "/simple-expenses/",
            json={
                "family_group_id": str(family_group.id),
                "amount": "10",
                "description": "July",
                "expense_date": "2026-07-10",
            },
            headers=client_auth_headers,
        )
        await client.post(
            "/simple-expenses/",
            json={
                "family_group_id": str(family_group.id),
                "amount": "20",
                "description": "August",
                "expense_date": "2026-08-10",
            },
            headers=client_auth_headers,
        )

        resp = await client.get(
            "/simple-expenses/",
            params={
                "family_group_id": str(family_group.id),
                "start_date": "2026-07-01",
                "end_date": "2026-07-31",
            },
            headers=client_auth_headers,
        )
        assert len(resp.json()) == 1
        assert resp.json()[0]["description"] == "July"

    async def test_delete_expense(
        self, client, client_auth_headers, family_group
    ):
        create_resp = await client.post(
            "/simple-expenses/",
            json={
                "family_group_id": str(family_group.id),
                "amount": "100",
                "description": "Delete me",
                "expense_date": "2026-07-01",
            },
            headers=client_auth_headers,
        )
        expense_id = create_resp.json()["id"]

        resp = await client.delete(
            f"/simple-expenses/{expense_id}",
            headers=client_auth_headers,
        )
        assert resp.status_code == 204

    async def test_delete_expense_not_found(
        self, client, client_auth_headers
    ):
        resp = await client.delete(
            f"/simple-expenses/{uuid.uuid4()}",
            headers=client_auth_headers,
        )
        assert resp.status_code == 404

    async def test_unauthorized(self, client):
        resp = await client.get(
            "/simple-expenses/",
            params={"family_group_id": str(uuid.uuid4())},
        )
        assert resp.status_code == 403