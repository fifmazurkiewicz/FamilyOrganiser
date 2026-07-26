"""Integration tests for Simple Investments API router."""

import uuid
from datetime import date
import pytest


class TestSimpleInvestmentAPI:
    async def test_create_investment(
        self, client, client_auth_headers, family_group
    ):
        resp = await client.post(
            "/simple-investments/",
            json={
                "family_group_id": str(family_group.id),
                "name": "Fixed Deposit",
                "investment_type": "deposit",
                "principal_amount": "10000.00",
                "interest_rate": "0.05",
                "interest_period": "yearly",
                "start_date": "2026-01-01",
                "duration_value": 3,
                "duration_unit": "years",
                "notes": "Safe",
            },
            headers=client_auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Fixed Deposit"
        assert data["investment_type"] == "deposit"
        assert data["principal_amount"] == "10000.00"
        assert data["end_date"] == "2029-01-01"
        assert data["projected_profit"] == "1500.00"
        assert data["projected_total"] == "11500.00"

    async def test_list_investments(
        self, client, client_auth_headers, family_group
    ):
        await client.post(
            "/simple-investments/",
            json={
                "family_group_id": str(family_group.id),
                "name": "Inv A",
                "investment_type": "deposit",
                "principal_amount": "1000",
                "interest_rate": "0.05",
                "interest_period": "yearly",
                "start_date": "2026-01-01",
                "duration_value": 1,
                "duration_unit": "years",
            },
            headers=client_auth_headers,
        )
        await client.post(
            "/simple-investments/",
            json={
                "family_group_id": str(family_group.id),
                "name": "Inv B",
                "investment_type": "bonds",
                "principal_amount": "2000",
                "interest_rate": "0.03",
                "interest_period": "yearly",
                "start_date": "2026-06-01",
                "duration_value": 6,
                "duration_unit": "months",
            },
            headers=client_auth_headers,
        )

        resp = await client.get(
            "/simple-investments/",
            params={"family_group_id": str(family_group.id)},
            headers=client_auth_headers,
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_get_investment(
        self, client, client_auth_headers, family_group
    ):
        create_resp = await client.post(
            "/simple-investments/",
            json={
                "family_group_id": str(family_group.id),
                "name": "Get Me",
                "investment_type": "stocks",
                "principal_amount": "500",
                "interest_rate": "0.10",
                "interest_period": "yearly",
                "start_date": "2026-01-01",
                "duration_value": 1,
                "duration_unit": "years",
            },
            headers=client_auth_headers,
        )
        inv_id = create_resp.json()["id"]

        resp = await client.get(
            f"/simple-investments/{inv_id}",
            headers=client_auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Get Me"

    async def test_get_investment_not_found(
        self, client, client_auth_headers
    ):
        resp = await client.get(
            f"/simple-investments/{uuid.uuid4()}",
            headers=client_auth_headers,
        )
        assert resp.status_code == 404

    async def test_update_investment(
        self, client, client_auth_headers, family_group
    ):
        create_resp = await client.post(
            "/simple-investments/",
            json={
                "family_group_id": str(family_group.id),
                "name": "Original",
                "investment_type": "deposit",
                "principal_amount": "10000",
                "interest_rate": "0.05",
                "interest_period": "yearly",
                "start_date": "2026-01-01",
                "duration_value": 1,
                "duration_unit": "years",
            },
            headers=client_auth_headers,
        )
        inv_id = create_resp.json()["id"]

        resp = await client.patch(
            f"/simple-investments/{inv_id}",
            json={
                "principal_amount": "20000",
                "interest_rate": "0.10",
                "duration_value": 2,
            },
            headers=client_auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["principal_amount"] == "20000"
        assert data["end_date"] == "2028-01-01"
        assert data["projected_profit"] == "4000"

    async def test_delete_investment(
        self, client, client_auth_headers, family_group
    ):
        create_resp = await client.post(
            "/simple-investments/",
            json={
                "family_group_id": str(family_group.id),
                "name": "Delete Me",
                "investment_type": "other",
                "principal_amount": "1",
                "interest_rate": "0.01",
                "interest_period": "yearly",
                "start_date": "2026-01-01",
                "duration_value": 1,
                "duration_unit": "months",
            },
            headers=client_auth_headers,
        )
        inv_id = create_resp.json()["id"]

        resp = await client.delete(
            f"/simple-investments/{inv_id}",
            headers=client_auth_headers,
        )
        assert resp.status_code == 204

        get_resp = await client.get(
            f"/simple-investments/{inv_id}",
            headers=client_auth_headers,
        )
        assert get_resp.status_code == 404

    async def test_get_summary(
        self, client, client_auth_headers, family_group
    ):
        await client.post(
            "/simple-investments/",
            json={
                "family_group_id": str(family_group.id),
                "name": "Inv 1",
                "investment_type": "deposit",
                "principal_amount": "1000",
                "interest_rate": "0.10",
                "interest_period": "yearly",
                "start_date": "2026-01-01",
                "duration_value": 1,
                "duration_unit": "years",
            },
            headers=client_auth_headers,
        )
        await client.post(
            "/simple-investments/",
            json={
                "family_group_id": str(family_group.id),
                "name": "Inv 2",
                "investment_type": "stocks",
                "principal_amount": "5000",
                "interest_rate": "0.15",
                "interest_period": "yearly",
                "start_date": "2026-01-01",
                "duration_value": 2,
                "duration_unit": "years",
            },
            headers=client_auth_headers,
        )

        resp = await client.get(
            "/simple-investments/summary",
            params={"family_group_id": str(family_group.id)},
            headers=client_auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_principal"] == "6000.00"
        assert data["total_projected_profit"] == "1600.00"
        assert data["total_projected_value"] == "7600.00"
        assert len(data["investments"]) == 2

    async def test_unauthorized(self, client):
        resp = await client.get(
            "/simple-investments/",
            params={"family_group_id": str(uuid.uuid4())},
        )
        assert resp.status_code == 403