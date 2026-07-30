"""Unit tests for SimpleInvestmentService — CRUD, auto-calculate end_date and profit, summary."""

import uuid
from datetime import date
from decimal import Decimal

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.simple_investment import (
    SimpleInvestmentService,
    _calculate_end_date,
    _calculate_profit,
)
from app.schemas.simple_investment import (
    SimpleInvestmentCreate,
    SimpleInvestmentUpdate,
)
from app.models.simple_investment import (
    SimpleInvestmentType,
    InterestPeriod,
    DurationUnit,
)
from app.core.exceptions import NotFoundError


# ── Pure-function helpers ──────────────────────────────────────

class TestCalculationHelpers:
    def test_end_date_months(self):
        result = _calculate_end_date(date(2026, 1, 15), 6, DurationUnit.MONTHS)
        assert result == date(2026, 7, 15)

    def test_end_date_years(self):
        result = _calculate_end_date(date(2026, 1, 1), 2, DurationUnit.YEARS)
        assert result == date(2028, 1, 1)

    def test_end_date_quarters(self):
        result = _calculate_end_date(date(2026, 1, 1), 4, DurationUnit.QUARTERS)
        assert result == date(2027, 1, 1)  # 12 months

    def test_profit_simple_yearly(self):
        profit = _calculate_profit(
            Decimal("10000"), Decimal("0.05"),
            InterestPeriod.YEARLY, 2, DurationUnit.YEARS,
        )
        # 10000 * 0.05 * 2 = 1000
        assert profit == Decimal("1000.00")

    def test_profit_simple_monthly(self):
        profit = _calculate_profit(
            Decimal("10000"), Decimal("0.12"),  # 12% annually
            InterestPeriod.MONTHLY, 6, DurationUnit.MONTHS,
        )
        # 10000 * 0.12 * (6/12) = 600
        assert profit == Decimal("600.00")

    def test_profit_simple_quarterly(self):
        profit = _calculate_profit(
            Decimal("5000"), Decimal("0.08"),
            InterestPeriod.QUARTERLY, 3, DurationUnit.QUARTERS,
        )
        # 5000 * 0.08 * (9/12) = 300
        assert profit == Decimal("300.00")


# ── Service CRUD tests ────────────────────────────────────────

class TestSimpleInvestmentCRUD:
    async def test_create_investment(
        self, db_session: AsyncSession, test_user, family_group
    ):
        svc = SimpleInvestmentService(db_session)
        data = SimpleInvestmentCreate(
            family_group_id=family_group.id,
            name="Fixed Deposit",
            investment_type=SimpleInvestmentType.DEPOSIT,
            principal_amount=Decimal("10000.00"),
            interest_rate=Decimal("0.05"),
            interest_period=InterestPeriod.YEARLY,
            start_date=date(2026, 1, 1),
            duration_value=3,
            duration_unit=DurationUnit.YEARS,
            notes="Safe investment",
        )
        result = await svc.create_investment(test_user.id, data)

        assert result.id is not None
        assert result.name == "Fixed Deposit"
        assert result.investment_type == SimpleInvestmentType.DEPOSIT
        assert result.principal_amount == Decimal("10000.00")
        assert result.interest_rate == Decimal("0.05")
        assert result.start_date == date(2026, 1, 1)
        assert result.duration_value == 3
        assert result.duration_unit == DurationUnit.YEARS
        assert result.end_date == date(2029, 1, 1)  # auto-calculated
        assert result.projected_profit == Decimal("1500.00")  # 10000 * 0.05 * 3
        assert result.projected_total == Decimal("11500.00")
        assert result.notes == "Safe investment"
        assert result.user_id == test_user.id

    async def test_create_investment_auto_calculates(
        self, db_session: AsyncSession, test_user, family_group
    ):
        """Verify end_date and profit are calculated automatically regardless of input."""
        svc = SimpleInvestmentService(db_session)
        data = SimpleInvestmentCreate(
            family_group_id=family_group.id,
            name="Auto Test",
            investment_type=SimpleInvestmentType.BONDS,
            principal_amount=Decimal("5000.00"),
            interest_rate=Decimal("0.10"),
            interest_period=InterestPeriod.YEARLY,
            start_date=date(2026, 6, 1),
            duration_value=12,
            duration_unit=DurationUnit.MONTHS,
        )
        result = await svc.create_investment(test_user.id, data)

        assert result.end_date == date(2027, 6, 1)
        assert result.projected_profit == Decimal("500.00")  # 5000 * 0.10 * 1
        assert result.projected_total == Decimal("5500.00")

    async def test_list_investments(
        self, db_session: AsyncSession, test_user, family_group
    ):
        svc = SimpleInvestmentService(db_session)
        await svc.create_investment(
            test_user.id,
            SimpleInvestmentCreate(
                family_group_id=family_group.id,
                name="Inv A",
                investment_type=SimpleInvestmentType.STOCKS,
                principal_amount=Decimal("1000"),
                interest_rate=Decimal("0.1"),
                start_date=date(2026, 1, 1),
                duration_value=1,
                duration_unit=DurationUnit.YEARS,
            ),
        )
        await svc.create_investment(
            test_user.id,
            SimpleInvestmentCreate(
                family_group_id=family_group.id,
                name="Inv B",
                investment_type=SimpleInvestmentType.DEPOSIT,
                principal_amount=Decimal("2000"),
                interest_rate=Decimal("0.05"),
                start_date=date(2026, 6, 1),
                duration_value=6,
                duration_unit=DurationUnit.MONTHS,
            ),
        )

        investments = await svc.list_investments(test_user.id, family_group.id)
        assert len(investments) == 2

    async def test_list_investments_family_isolation(
        self, db_session: AsyncSession, test_user, test_user2, family_group, family_group2
    ):
        svc = SimpleInvestmentService(db_session)
        await svc.create_investment(
            test_user.id,
            SimpleInvestmentCreate(
                family_group_id=family_group.id,
                name="F1 Only",
                investment_type=SimpleInvestmentType.OTHER,
                principal_amount=Decimal("100"),
                interest_rate=Decimal("0.01"),
                start_date=date(2026, 1, 1),
                duration_value=1,
                duration_unit=DurationUnit.MONTHS,
            ),
        )
        await svc.create_investment(
            test_user2.id,
            SimpleInvestmentCreate(
                family_group_id=family_group2.id,
                name="F2 Only",
                investment_type=SimpleInvestmentType.OTHER,
                principal_amount=Decimal("200"),
                interest_rate=Decimal("0.01"),
                start_date=date(2026, 1, 1),
                duration_value=1,
                duration_unit=DurationUnit.MONTHS,
            ),
        )

        f1 = await svc.list_investments(test_user.id, family_group.id)
        f2 = await svc.list_investments(test_user2.id, family_group2.id)

        assert len(f1) == 1
        assert f1[0].name == "F1 Only"
        assert len(f2) == 1
        assert f2[0].name == "F2 Only"

    async def test_get_investment(
        self, db_session: AsyncSession, test_user, family_group
    ):
        svc = SimpleInvestmentService(db_session)
        created = await svc.create_investment(
            test_user.id,
            SimpleInvestmentCreate(
                family_group_id=family_group.id,
                name="Get Me",
                investment_type=SimpleInvestmentType.BONDS,
                principal_amount=Decimal("500"),
                interest_rate=Decimal("0.03"),
                start_date=date(2026, 1, 1),
                duration_value=1,
                duration_unit=DurationUnit.YEARS,
            ),
        )
        fetched = await svc.get_investment(test_user.id, created.id)
        assert fetched.id == created.id
        assert fetched.name == "Get Me"

    async def test_get_investment_not_found(
        self, db_session: AsyncSession, test_user, family_group
    ):
        svc = SimpleInvestmentService(db_session)
        with pytest.raises(NotFoundError):
            await svc.get_investment(test_user.id, uuid.uuid4())

    async def test_update_investment_recalculates(
        self, db_session: AsyncSession, test_user, family_group
    ):
        svc = SimpleInvestmentService(db_session)
        created = await svc.create_investment(
            test_user.id,
            SimpleInvestmentCreate(
                family_group_id=family_group.id,
                name="Original",
                investment_type=SimpleInvestmentType.DEPOSIT,
                principal_amount=Decimal("10000"),
                interest_rate=Decimal("0.05"),
                start_date=date(2026, 1, 1),
                duration_value=1,
                duration_unit=DurationUnit.YEARS,
            ),
        )

        updated = await svc.update_investment(test_user.id, created.id,
            SimpleInvestmentUpdate(
                principal_amount=Decimal("20000"),
                interest_rate=Decimal("0.10"),
                duration_value=2,
            ),
        )

        assert updated.principal_amount == Decimal("20000")
        assert updated.interest_rate == Decimal("0.10")
        assert updated.end_date == date(2028, 1, 1)  # recalculated
        assert updated.projected_profit == Decimal("4000.00")  # 20000 * 0.10 * 2
        assert updated.projected_total == Decimal("24000.00")
        assert updated.name == "Original"  # unchanged

    async def test_delete_investment(
        self, db_session: AsyncSession, test_user, family_group
    ):
        svc = SimpleInvestmentService(db_session)
        created = await svc.create_investment(
            test_user.id,
            SimpleInvestmentCreate(
                family_group_id=family_group.id,
                name="Delete Me",
                investment_type=SimpleInvestmentType.OTHER,
                principal_amount=Decimal("1"),
                interest_rate=Decimal("0.01"),
                start_date=date(2026, 1, 1),
                duration_value=1,
                duration_unit=DurationUnit.MONTHS,
            ),
        )
        await svc.delete_investment(test_user.id, created.id)

        with pytest.raises(NotFoundError):
            await svc.get_investment(test_user.id, created.id)

    async def test_delete_investment_not_found(
        self, db_session: AsyncSession, test_user, family_group
    ):
        svc = SimpleInvestmentService(db_session)
        with pytest.raises(NotFoundError):
            await svc.delete_investment(test_user.id, uuid.uuid4())


# ── Summary ────────────────────────────────────────────────────

class TestInvestmentSummary:
    async def test_summary_aggregation(
        self, db_session: AsyncSession, test_user, family_group
    ):
        svc = SimpleInvestmentService(db_session)
        await svc.create_investment(
            test_user.id,
            SimpleInvestmentCreate(
                family_group_id=family_group.id,
                name="Inv 1",
                investment_type=SimpleInvestmentType.DEPOSIT,
                principal_amount=Decimal("1000"),
                interest_rate=Decimal("0.10"),
                start_date=date(2026, 1, 1),
                duration_value=1,
                duration_unit=DurationUnit.YEARS,
            ),
        )
        await svc.create_investment(
            test_user.id,
            SimpleInvestmentCreate(
                family_group_id=family_group.id,
                name="Inv 2",
                investment_type=SimpleInvestmentType.STOCKS,
                principal_amount=Decimal("5000"),
                interest_rate=Decimal("0.15"),
                start_date=date(2026, 1, 1),
                duration_value=2,
                duration_unit=DurationUnit.YEARS,
            ),
        )

        summary = await svc.get_summary(test_user.id, family_group.id)

        assert summary.total_principal == Decimal("6000.00")
        # Inv 1: 1000 * 0.10 * 1 = 100, Inv 2: 5000 * 0.15 * 2 = 1500
        assert summary.total_projected_profit == Decimal("1600.00")
        assert summary.total_projected_value == Decimal("7600.00")
        assert len(summary.investments) == 2

    async def test_summary_empty(self, db_session: AsyncSession, test_user, family_group):
        svc = SimpleInvestmentService(db_session)
        summary = await svc.get_summary(test_user.id, family_group.id)
        assert summary.total_principal == Decimal("0")
        assert summary.total_projected_profit == Decimal("0")
        assert summary.total_projected_value == Decimal("0")
        assert summary.investments == []