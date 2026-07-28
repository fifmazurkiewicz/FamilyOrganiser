"""Integration tests for Reports API."""

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.family import FamilyMembership, FamilyRole
from app.models.monthly_budget import BudgetEntry, BudgetEntryType, MonthlyBudget


class TestReportsAPI:
    async def test_dashboard_empty(self, client, client_auth_headers):
        resp = await client.get("/reports/dashboard", headers=client_auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["monthly_income"] == 0
        assert data["monthly_expenses"] == 0

    async def test_dashboard_with_budget_data(
        self, client, client_auth_headers, db_session: AsyncSession, test_user, family_group
    ):
        db_session.add(
            FamilyMembership(
                user_id=test_user.id,
                family_group_id=family_group.id,
                role=FamilyRole.ADMIN,
            )
        )
        today = date.today()
        budget = MonthlyBudget(
            family_group_id=family_group.id, year=today.year, month=today.month
        )
        db_session.add(budget)
        await db_session.flush()
        db_session.add(
            BudgetEntry(
                budget_id=budget.id,
                entry_type=BudgetEntryType.INCOME,
                name="Pensja",
                amount=Decimal("4000"),
                is_recurring=False,
                created_by=test_user.id,
            )
        )
        db_session.add(
            BudgetEntry(
                budget_id=budget.id,
                entry_type=BudgetEntryType.EXPENSE,
                name="Czynsz",
                amount=Decimal("1500"),
                is_recurring=False,
                created_by=test_user.id,
            )
        )
        await db_session.flush()

        resp = await client.get("/reports/dashboard", headers=client_auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["monthly_income"] == 4000
        assert data["monthly_expenses"] == 1500
        assert data["savings_rate"] == 62.5

    async def test_expenses_by_category(
        self, client, client_auth_headers, db_session: AsyncSession, test_user, family_group
    ):
        db_session.add(
            FamilyMembership(
                user_id=test_user.id,
                family_group_id=family_group.id,
                role=FamilyRole.ADMIN,
            )
        )
        today = date.today()
        budget = MonthlyBudget(
            family_group_id=family_group.id, year=today.year, month=today.month
        )
        db_session.add(budget)
        await db_session.flush()
        db_session.add(
            BudgetEntry(
                budget_id=budget.id,
                entry_type=BudgetEntryType.EXPENSE,
                name="Jedzenie",
                amount=Decimal("320"),
                is_recurring=False,
                created_by=test_user.id,
            )
        )
        await db_session.flush()

        resp = await client.get(
            "/reports/expenses-by-category",
            params={"year": today.year, "month": today.month},
            headers=client_auth_headers,
        )
        assert resp.status_code == 200
        rows = resp.json()
        assert any(r["category"] == "Jedzenie" and float(r["amount"]) == 320 for r in rows)

    async def test_monthly_trend(self, client, client_auth_headers):
        resp = await client.get(
            "/reports/monthly-trend",
            params={"months": 6},
            headers=client_auth_headers,
        )
        assert resp.status_code == 200
        trend = resp.json()
        assert len(trend) == 6
        assert "month" in trend[0]
        assert "income" in trend[0]
        assert "expenses" in trend[0]
