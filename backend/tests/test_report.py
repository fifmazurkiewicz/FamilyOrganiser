"""Unit tests for ReportService — dashboard, categories, trend from monthly budgets."""

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.family import FamilyMembership, FamilyRole
from app.models.monthly_budget import BudgetEntry, BudgetEntryType, MonthlyBudget
from app.models.simple_investment import (
    DurationUnit,
    InterestPeriod,
    SimpleInvestment,
    SimpleInvestmentType,
)
from app.services.report import ReportService


async def _add_membership(db: AsyncSession, user_id, group_id) -> None:
    db.add(
        FamilyMembership(
            user_id=user_id,
            family_group_id=group_id,
            role=FamilyRole.ADMIN,
        )
    )
    await db.flush()


async def _seed_budget_with_entries(
    db: AsyncSession,
    *,
    group_id,
    user_id,
    year: int,
    month: int,
    income: Decimal,
    expense: Decimal,
    expense_name: str = "Rent",
) -> MonthlyBudget:
    budget = MonthlyBudget(family_group_id=group_id, year=year, month=month)
    db.add(budget)
    await db.flush()
    db.add(
        BudgetEntry(
            budget_id=budget.id,
            entry_type=BudgetEntryType.INCOME,
            name="Salary",
            amount=income,
            is_recurring=False,
            created_by=user_id,
        )
    )
    db.add(
        BudgetEntry(
            budget_id=budget.id,
            entry_type=BudgetEntryType.EXPENSE,
            name=expense_name,
            amount=expense,
            is_recurring=False,
            created_by=user_id,
        )
    )
    await db.flush()
    return budget


class TestReportDashboard:
    async def test_dashboard_empty_when_no_groups(
        self, db_session: AsyncSession, test_user
    ):
        svc = ReportService(db_session)
        data = await svc.dashboard(test_user.id)

        assert data["monthly_income"] == 0.0
        assert data["monthly_expenses"] == 0.0
        assert data["net_worth"] == 0.0
        assert data["savings_rate"] == 0.0
        assert data["top_expenses"] == []
        assert data["total_assets"] == 0.0

    async def test_dashboard_from_monthly_budget(
        self, db_session: AsyncSession, test_user, family_group
    ):
        await _add_membership(db_session, test_user.id, family_group.id)
        today = date.today()
        await _seed_budget_with_entries(
            db_session,
            group_id=family_group.id,
            user_id=test_user.id,
            year=today.year,
            month=today.month,
            income=Decimal("5000.00"),
            expense=Decimal("2000.00"),
        )

        svc = ReportService(db_session)
        data = await svc.dashboard(test_user.id)

        assert data["monthly_income"] == 5000.0
        assert data["monthly_expenses"] == 2000.0
        assert data["savings_rate"] == 60.0
        assert data["net_worth"] == 3000.0
        assert len(data["top_expenses"]) == 1
        assert data["top_expenses"][0]["category"] == "Rent"
        assert data["top_expenses"][0]["amount"] == 2000.0

    async def test_dashboard_includes_investments(
        self, db_session: AsyncSession, test_user, family_group
    ):
        await _add_membership(db_session, test_user.id, family_group.id)
        today = date.today()
        await _seed_budget_with_entries(
            db_session,
            group_id=family_group.id,
            user_id=test_user.id,
            year=today.year,
            month=today.month,
            income=Decimal("1000.00"),
            expense=Decimal("100.00"),
        )
        db_session.add(
            SimpleInvestment(
                family_group_id=family_group.id,
                user_id=test_user.id,
                name="Lokata",
                investment_type=SimpleInvestmentType.DEPOSIT,
                principal_amount=Decimal("10000.00"),
                interest_rate=Decimal("0.05"),
                interest_period=InterestPeriod.YEARLY,
                start_date=today,
                duration_value=12,
                duration_unit=DurationUnit.MONTHS,
                end_date=today,
                projected_profit=Decimal("500"),
                projected_total=Decimal("10500"),
            )
        )
        await db_session.flush()

        svc = ReportService(db_session)
        data = await svc.dashboard(test_user.id)

        assert data["total_assets"] == 10000.0
        assert data["net_worth"] == 10900.0  # 1000 - 100 + 10000


class TestExpensesByCategory:
    async def test_groups_expenses_by_name(
        self, db_session: AsyncSession, test_user, family_group
    ):
        await _add_membership(db_session, test_user.id, family_group.id)
        today = date.today()
        budget = MonthlyBudget(
            family_group_id=family_group.id, year=today.year, month=today.month
        )
        db_session.add(budget)
        await db_session.flush()
        for name, amount in [("Food", "100"), ("Food", "50"), ("Transport", "80")]:
            db_session.add(
                BudgetEntry(
                    budget_id=budget.id,
                    entry_type=BudgetEntryType.EXPENSE,
                    name=name,
                    amount=Decimal(amount),
                    is_recurring=False,
                    created_by=test_user.id,
                )
            )
        await db_session.flush()

        svc = ReportService(db_session)
        rows = await svc.expenses_by_category(test_user.id, today.year, today.month)

        by_name = {r["category"]: r["amount"] for r in rows}
        assert by_name["Food"] == 150.0
        assert by_name["Transport"] == 80.0
        assert rows[0]["amount"] >= rows[-1]["amount"]

    async def test_empty_without_membership(
        self, db_session: AsyncSession, test_user, family_group
    ):
        svc = ReportService(db_session)
        rows = await svc.expenses_by_category(
            test_user.id, date.today().year, date.today().month
        )
        assert rows == []


class TestMonthlyTrend:
    async def test_trend_length_and_shape(
        self, db_session: AsyncSession, test_user, family_group
    ):
        await _add_membership(db_session, test_user.id, family_group.id)
        today = date.today()
        await _seed_budget_with_entries(
            db_session,
            group_id=family_group.id,
            user_id=test_user.id,
            year=today.year,
            month=today.month,
            income=Decimal("3000"),
            expense=Decimal("1000"),
        )

        svc = ReportService(db_session)
        trend = await svc.monthly_trend(test_user.id, months=3)

        assert len(trend) == 3
        assert all(set(item) >= {"month", "income", "expenses", "savings"} for item in trend)
        current = trend[-1]
        assert current["month"] == f"{today.year}-{today.month:02d}"
        assert current["income"] == 3000.0
        assert current["expenses"] == 1000.0
        assert current["savings"] == 2000.0
