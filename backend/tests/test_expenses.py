"""Unit tests for SimpleExpenseService — create, list by month, delete."""

import uuid
from datetime import date
from decimal import Decimal

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.expense import SimpleExpenseService
from app.schemas.expense import SimpleExpenseCreate
from app.core.exceptions import NotFoundError, ForbiddenError


class TestSimpleExpenseService:
    async def test_create_expense(self, db_session: AsyncSession, test_user, family_group):
        svc = SimpleExpenseService(db_session)
        data = SimpleExpenseCreate(
            family_group_id=family_group.id,
            amount=Decimal("42.50"),
            description="Groceries at Lidl",
            expense_date=date(2026, 7, 20),
        )
        result = await svc.create_expense(test_user.id, data)

        assert result.id is not None
        assert result.amount == Decimal("42.50")
        assert result.description == "Groceries at Lidl"
        assert result.expense_date == date(2026, 7, 20)
        assert result.user_id == test_user.id
        assert result.family_group_id == family_group.id

    async def test_list_expenses(self, db_session: AsyncSession, test_user, family_group):
        svc = SimpleExpenseService(db_session)
        await svc.create_expense(
            test_user.id,
            SimpleExpenseCreate(
                family_group_id=family_group.id,
                amount=Decimal("10"),
                description="A",
                expense_date=date(2026, 7, 1),
            ),
        )
        await svc.create_expense(
            test_user.id,
            SimpleExpenseCreate(
                family_group_id=family_group.id,
                amount=Decimal("20"),
                description="B",
                expense_date=date(2026, 7, 15),
            ),
        )
        await svc.create_expense(
            test_user.id,
            SimpleExpenseCreate(
                family_group_id=family_group.id,
                amount=Decimal("30"),
                description="C",
                expense_date=date(2026, 8, 1),
            ),
        )

        all_expenses = await svc.list_expenses(family_group.id)
        assert len(all_expenses) == 3

    async def test_list_expenses_date_filter(self, db_session: AsyncSession, test_user, family_group):
        svc = SimpleExpenseService(db_session)
        await svc.create_expense(
            test_user.id,
            SimpleExpenseCreate(
                family_group_id=family_group.id,
                amount=Decimal("10"),
                description="July",
                expense_date=date(2026, 7, 10),
            ),
        )
        await svc.create_expense(
            test_user.id,
            SimpleExpenseCreate(
                family_group_id=family_group.id,
                amount=Decimal("20"),
                description="August",
                expense_date=date(2026, 8, 10),
            ),
        )

        july = await svc.list_expenses(
            family_group.id,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 31),
        )
        assert len(july) == 1
        assert july[0].description == "July"

    async def test_list_expenses_family_isolation(
        self, db_session: AsyncSession, test_user, family_group, family_group2
    ):
        svc = SimpleExpenseService(db_session)
        await svc.create_expense(
            test_user.id,
            SimpleExpenseCreate(
                family_group_id=family_group.id,
                amount=Decimal("10"),
                description="F1",
                expense_date=date(2026, 7, 1),
            ),
        )
        await svc.create_expense(
            test_user.id,
            SimpleExpenseCreate(
                family_group_id=family_group2.id,
                amount=Decimal("20"),
                description="F2",
                expense_date=date(2026, 7, 1),
            ),
        )

        f1 = await svc.list_expenses(family_group.id)
        f2 = await svc.list_expenses(family_group2.id)

        assert len(f1) == 1
        assert f1[0].description == "F1"
        assert len(f2) == 1
        assert f2[0].description == "F2"

    async def test_delete_expense_owner(self, db_session: AsyncSession, test_user, family_group):
        svc = SimpleExpenseService(db_session)
        created = await svc.create_expense(
            test_user.id,
            SimpleExpenseCreate(
                family_group_id=family_group.id,
                amount=Decimal("100"),
                description="Delete me",
                expense_date=date(2026, 7, 1),
            ),
        )
        await svc.delete_expense(test_user.id, created.id)

        # Verify it's gone
        remaining = await svc.list_expenses(family_group.id)
        assert len(remaining) == 0

    async def test_delete_expense_not_found(self, db_session: AsyncSession, test_user, family_group):
        svc = SimpleExpenseService(db_session)
        with pytest.raises(NotFoundError):
            await svc.delete_expense(test_user.id, uuid.uuid4())

    async def test_delete_expense_not_owner(
        self, db_session: AsyncSession, test_user, test_user2, family_group
    ):
        svc = SimpleExpenseService(db_session)
        created = await svc.create_expense(
            test_user.id,
            SimpleExpenseCreate(
                family_group_id=family_group.id,
                amount=Decimal("100"),
                description="Not yours",
                expense_date=date(2026, 7, 1),
            ),
        )
        # test_user2 tries to delete test_user's expense
        with pytest.raises(ForbiddenError):
            await svc.delete_expense(test_user2.id, created.id)