"""Unit tests for MonthlyBudgetService — create budget, add entries, summary, recurring copy."""

import uuid
from decimal import Decimal

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.monthly_budget import MonthlyBudgetService
from app.schemas.monthly_budget import (
    MonthlyBudgetCreate,
    BudgetEntryCreate,
)
from app.models.monthly_budget import BudgetEntryType
from app.core.exceptions import NotFoundError


class TestMonthlyBudgetCreate:
    async def test_create_new_budget(self, db_session: AsyncSession, test_user, family_group):
        svc = MonthlyBudgetService(db_session)
        data = MonthlyBudgetCreate(
            family_group_id=family_group.id, year=2026, month=7
        )
        result = await svc.get_or_create_budget(test_user.id, data)

        assert result.id is not None
        assert result.family_group_id == family_group.id
        assert result.year == 2026
        assert result.month == 7
        assert result.entries == []

    async def test_get_or_create_returns_existing(
        self, db_session: AsyncSession, test_user, family_group
    ):
        svc = MonthlyBudgetService(db_session)
        data = MonthlyBudgetCreate(
            family_group_id=family_group.id, year=2026, month=7
        )
        first = await svc.get_or_create_budget(test_user.id, data)
        second = await svc.get_or_create_budget(test_user.id, data)

        assert first.id == second.id  # Same budget

    async def test_get_budget(self, db_session: AsyncSession, test_user, family_group):
        svc = MonthlyBudgetService(db_session)
        data = MonthlyBudgetCreate(family_group_id=family_group.id, year=2026, month=3)
        created = await svc.get_or_create_budget(test_user.id, data)
        fetched = await svc.get_budget(created.id)
        assert fetched.id == created.id

    async def test_get_budget_not_found(self, db_session: AsyncSession, test_user, family_group):
        svc = MonthlyBudgetService(db_session)
        with pytest.raises(NotFoundError):
            await svc.get_budget(uuid.uuid4())

    async def test_get_budget_for_month(self, db_session: AsyncSession, test_user, family_group):
        svc = MonthlyBudgetService(db_session)
        await svc.get_or_create_budget(
            test_user.id,
            MonthlyBudgetCreate(family_group_id=family_group.id, year=2026, month=5),
        )

        found = await svc.get_budget_for_month(test_user.id, family_group.id, 2026, 5)
        assert found is not None
        assert found.year == 2026
        assert found.month == 5

        not_found = await svc.get_budget_for_month(test_user.id, family_group.id, 2025, 1)
        assert not_found is None


class TestBudgetEntries:
    @pytest_asyncio.fixture
    async def budget(self, db_session: AsyncSession, test_user, family_group):
        svc = MonthlyBudgetService(db_session)
        return await svc.get_or_create_budget(
            test_user.id,
            MonthlyBudgetCreate(family_group_id=family_group.id, year=2026, month=7),
        )

    async def test_add_entry_income(self, db_session: AsyncSession, test_user, budget):
        svc = MonthlyBudgetService(db_session)
        data = BudgetEntryCreate(
            entry_type=BudgetEntryType.INCOME,
            name="Salary",
            amount=Decimal("5000.00"),
            is_recurring=True,
        )
        entry = await svc.add_entry(test_user.id, budget.id, data)

        assert entry.id is not None
        assert entry.entry_type == BudgetEntryType.INCOME
        assert entry.name == "Salary"
        assert entry.amount == Decimal("5000.00")
        assert entry.is_recurring is True
        assert entry.created_by == test_user.id

    async def test_add_entry_expense(self, db_session: AsyncSession, test_user, budget):
        svc = MonthlyBudgetService(db_session)
        data = BudgetEntryCreate(
            entry_type=BudgetEntryType.EXPENSE,
            name="Rent",
            amount=Decimal("2500.00"),
            is_recurring=True,
        )
        entry = await svc.add_entry(test_user.id, budget.id, data)
        assert entry.entry_type == BudgetEntryType.EXPENSE
        assert entry.amount == Decimal("2500.00")

    async def test_update_entry(self, db_session: AsyncSession, test_user, budget):
        svc = MonthlyBudgetService(db_session)
        created = await svc.add_entry(
            test_user.id,
            budget.id,
            BudgetEntryCreate(
                entry_type=BudgetEntryType.INCOME,
                name="Old Name",
                amount=Decimal("100"),
                is_recurring=False,
            ),
        )
        updated = await svc.update_entry(
            test_user.id,
            created.id,
            BudgetEntryCreate(
                entry_type=BudgetEntryType.EXPENSE,
                name="Updated Name",
                amount=Decimal("200"),
                is_recurring=True,
            ),
        )
        assert updated.name == "Updated Name"
        assert updated.amount == Decimal("200")
        assert updated.entry_type == BudgetEntryType.EXPENSE
        assert updated.is_recurring is True

    async def test_remove_entry(self, db_session: AsyncSession, test_user, budget):
        svc = MonthlyBudgetService(db_session)
        entry = await svc.add_entry(
            test_user.id,
            budget.id,
            BudgetEntryCreate(
                entry_type=BudgetEntryType.INCOME,
                name="Temp",
                amount=Decimal("50"),
                is_recurring=False,
            ),
        )
        await svc.remove_entry(test_user.id, entry.id)

        with pytest.raises(NotFoundError):
            await svc.remove_entry(test_user.id, entry.id)  # Now missing

    async def test_remove_entry_not_found(self, db_session: AsyncSession, test_user, budget):
        svc = MonthlyBudgetService(db_session)
        with pytest.raises(NotFoundError):
            await svc.remove_entry(test_user.id, uuid.uuid4())


class TestBudgetSummary:
    async def test_summary_calculation(self, db_session: AsyncSession, test_user, family_group):
        svc = MonthlyBudgetService(db_session)
        budget = await svc.get_or_create_budget(
            test_user.id,
            MonthlyBudgetCreate(family_group_id=family_group.id, year=2026, month=7),
        )
        await svc.add_entry(
            test_user.id,
            budget.id,
            BudgetEntryCreate(
                entry_type=BudgetEntryType.INCOME,
                name="Salary",
                amount=Decimal("6000.00"),
                is_recurring=False,
            ),
        )
        await svc.add_entry(
            test_user.id,
            budget.id,
            BudgetEntryCreate(
                entry_type=BudgetEntryType.INCOME,
                name="Freelance",
                amount=Decimal("1000.00"),
                is_recurring=False,
            ),
        )
        await svc.add_entry(
            test_user.id,
            budget.id,
            BudgetEntryCreate(
                entry_type=BudgetEntryType.EXPENSE,
                name="Rent",
                amount=Decimal("2500.00"),
                is_recurring=False,
            ),
        )
        await svc.add_entry(
            test_user.id,
            budget.id,
            BudgetEntryCreate(
                entry_type=BudgetEntryType.EXPENSE,
                name="Food",
                amount=Decimal("1500.00"),
                is_recurring=False,
            ),
        )

        summary = await svc.get_summary(test_user.id, budget.id)

        assert summary.total_income == Decimal("7000.00")
        assert summary.total_expenses == Decimal("4000.00")
        assert summary.remaining == Decimal("3000.00")

    async def test_summary_empty_budget(self, db_session: AsyncSession, test_user, family_group):
        svc = MonthlyBudgetService(db_session)
        budget = await svc.get_or_create_budget(
            test_user.id,
            MonthlyBudgetCreate(family_group_id=family_group.id, year=2026, month=7),
        )
        summary = await svc.get_summary(test_user.id, budget.id)
        assert summary.total_income == Decimal("0")
        assert summary.total_expenses == Decimal("0")
        assert summary.remaining == Decimal("0")


class TestRecurringCopy:
    async def test_recurring_entries_copied_from_previous_month(
        self, db_session: AsyncSession, test_user, family_group
    ):
        svc = MonthlyBudgetService(db_session)

        # Create July budget with recurring entries
        july = await svc.get_or_create_budget(
            test_user.id,
            MonthlyBudgetCreate(family_group_id=family_group.id, year=2026, month=7),
        )
        await svc.add_entry(
            test_user.id,
            july.id,
            BudgetEntryCreate(
                entry_type=BudgetEntryType.INCOME,
                name="Salary",
                amount=Decimal("5000.00"),
                is_recurring=True,
            ),
        )
        await svc.add_entry(
            test_user.id,
            july.id,
            BudgetEntryCreate(
                entry_type=BudgetEntryType.EXPENSE,
                name="Rent",
                amount=Decimal("2000.00"),
                is_recurring=True,
            ),
        )
        await svc.add_entry(
            test_user.id,
            july.id,
            BudgetEntryCreate(
                entry_type=BudgetEntryType.EXPENSE,
                name="One-time purchase",
                amount=Decimal("100.00"),
                is_recurring=False,
            ),
        )

        # Create August — should copy recurring entries
        august = await svc.get_or_create_budget(
            test_user.id,
            MonthlyBudgetCreate(family_group_id=family_group.id, year=2026, month=8),
        )

        assert len(august.entries) == 2
        names = {e.name for e in august.entries}
        assert names == {"Salary", "Rent"}
        for e in august.entries:
            assert e.is_recurring is True

    async def test_year_crossover_recurring(
        self, db_session: AsyncSession, test_user, family_group
    ):
        svc = MonthlyBudgetService(db_session)

        # Create December budget
        dec = await svc.get_or_create_budget(
            test_user.id,
            MonthlyBudgetCreate(family_group_id=family_group.id, year=2026, month=12),
        )
        await svc.add_entry(
            test_user.id,
            dec.id,
            BudgetEntryCreate(
                entry_type=BudgetEntryType.INCOME,
                name="Yearly bonus",
                amount=Decimal("1000.00"),
                is_recurring=True,
            ),
        )

        # Create January 2027 — should copy from Dec 2026
        jan = await svc.get_or_create_budget(
            test_user.id,
            MonthlyBudgetCreate(family_group_id=family_group.id, year=2027, month=1),
        )

        assert len(jan.entries) == 1
        assert jan.entries[0].name == "Yearly bonus"

    async def test_no_recurring_when_no_previous_month(
        self, db_session: AsyncSession, test_user, family_group
    ):
        svc = MonthlyBudgetService(db_session)

        # First budget — no previous month exists
        first = await svc.get_or_create_budget(
            test_user.id,
            MonthlyBudgetCreate(family_group_id=family_group.id, year=2026, month=1),
        )
        assert first.entries == []