"""Integration tests for Monthly Budgets API router."""

import uuid
import pytest


class TestMonthlyBudgetAPI:
    async def test_create_budget(
        self, client, client_auth_headers, family_group
    ):
        resp = await client.post(
            "/monthly-budgets/",
            json={
                "family_group_id": str(family_group.id),
                "year": 2026,
                "month": 7,
            },
            headers=client_auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["year"] == 2026
        assert data["month"] == 7
        assert data["entries"] == []

    async def test_create_returns_existing(
        self, client, client_auth_headers, family_group
    ):
        data = {
            "family_group_id": str(family_group.id),
            "year": 2026,
            "month": 7,
        }
        first = await client.post(
            "/monthly-budgets/", json=data, headers=client_auth_headers
        )
        second = await client.post(
            "/monthly-budgets/", json=data, headers=client_auth_headers
        )
        assert first.json()["id"] == second.json()["id"]

    async def test_get_by_month(
        self, client, client_auth_headers, family_group
    ):
        resp = await client.get(
            "/monthly-budgets/by-month",
            params={
                "family_group_id": str(family_group.id),
                "year": 2026,
                "month": 7,
            },
            headers=client_auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["year"] == 2026

    async def test_add_entry(
        self, client, client_auth_headers, family_group
    ):
        budget_resp = await client.post(
            "/monthly-budgets/",
            json={
                "family_group_id": str(family_group.id),
                "year": 2026,
                "month": 7,
            },
            headers=client_auth_headers,
        )
        budget_id = budget_resp.json()["id"]

        resp = await client.post(
            f"/monthly-budgets/{budget_id}/entries",
            json={
                "entry_type": "income",
                "name": "Salary",
                "amount": "5000.00",
                "is_recurring": True,
            },
            headers=client_auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["entry_type"] == "income"
        assert data["name"] == "Salary"
        assert data["amount"] == "5000.00"
        assert data["is_recurring"] is True

    async def test_update_entry(
        self, client, client_auth_headers, family_group
    ):
        budget_resp = await client.post(
            "/monthly-budgets/",
            json={
                "family_group_id": str(family_group.id),
                "year": 2026,
                "month": 7,
            },
            headers=client_auth_headers,
        )
        budget_id = budget_resp.json()["id"]

        entry_resp = await client.post(
            f"/monthly-budgets/{budget_id}/entries",
            json={
                "entry_type": "income",
                "name": "Old",
                "amount": "100",
                "is_recurring": False,
            },
            headers=client_auth_headers,
        )
        entry_id = entry_resp.json()["id"]

        resp = await client.put(
            f"/monthly-budgets/entries/{entry_id}",
            json={
                "entry_type": "expense",
                "name": "Updated",
                "amount": "200",
                "is_recurring": True,
            },
            headers=client_auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Updated"
        assert data["amount"] == "200.00"

    async def test_delete_entry(
        self, client, client_auth_headers, family_group
    ):
        budget_resp = await client.post(
            "/monthly-budgets/",
            json={
                "family_group_id": str(family_group.id),
                "year": 2026,
                "month": 7,
            },
            headers=client_auth_headers,
        )
        budget_id = budget_resp.json()["id"]

        entry_resp = await client.post(
            f"/monthly-budgets/{budget_id}/entries",
            json={
                "entry_type": "income",
                "name": "Temp",
                "amount": "50",
                "is_recurring": False,
            },
            headers=client_auth_headers,
        )
        entry_id = entry_resp.json()["id"]

        resp = await client.delete(
            f"/monthly-budgets/entries/{entry_id}",
            headers=client_auth_headers,
        )
        assert resp.status_code == 204

    async def test_get_summary(
        self, client, client_auth_headers, family_group
    ):
        budget_resp = await client.post(
            "/monthly-budgets/",
            json={
                "family_group_id": str(family_group.id),
                "year": 2026,
                "month": 7,
            },
            headers=client_auth_headers,
        )
        budget_id = budget_resp.json()["id"]

        await client.post(
            f"/monthly-budgets/{budget_id}/entries",
            json={
                "entry_type": "income",
                "name": "Salary",
                "amount": "6000",
                "is_recurring": False,
            },
            headers=client_auth_headers,
        )
        await client.post(
            f"/monthly-budgets/{budget_id}/entries",
            json={
                "entry_type": "expense",
                "name": "Rent",
                "amount": "2000",
                "is_recurring": False,
            },
            headers=client_auth_headers,
        )

        resp = await client.get(
            f"/monthly-budgets/{budget_id}/summary",
            headers=client_auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_income"] == "6000.00"
        assert data["total_expenses"] == "2000.00"
        assert data["remaining"] == "4000.00"

    async def test_unauthorized(self, client):
        resp = await client.post(
            "/monthly-budgets/",
            json={
                "family_group_id": str(uuid.uuid4()),
                "year": 2026,
                "month": 1,
            },
        )
        assert resp.status_code == 403