"""Simple investment service."""
import uuid
from datetime import date
from decimal import Decimal
from typing import List

from dateutil.relativedelta import relativedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.simple_investment import DurationUnit, InterestPeriod, SimpleInvestment
from app.schemas.simple_investment import (
    InvestmentSummaryResponse,
    SimpleInvestmentCreate,
    SimpleInvestmentResponse,
    SimpleInvestmentUpdate,
)
from app.services.group_access import require_family_member


def _calculate_end_date(start_date: date, duration_value: int, duration_unit: DurationUnit) -> date:
    if duration_unit == DurationUnit.MONTHS:
        return start_date + relativedelta(months=duration_value)
    elif duration_unit == DurationUnit.QUARTERS:
        return start_date + relativedelta(months=duration_value * 3)
    return start_date + relativedelta(years=duration_value)


def _calculate_profit(
    principal: Decimal, rate: Decimal, period: InterestPeriod,
    duration_value: int, duration_unit: DurationUnit,
) -> Decimal:
    if duration_unit == DurationUnit.MONTHS:
        years = Decimal(duration_value) / Decimal(12)
    elif duration_unit == DurationUnit.QUARTERS:
        years = Decimal(duration_value * 3) / Decimal(12)
    else:
        years = Decimal(duration_value)

    return principal * rate * years


class SimpleInvestmentService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_investment(
        self, user_id: uuid.UUID, data: SimpleInvestmentCreate
    ) -> SimpleInvestmentResponse:
        await require_family_member(self._session, user_id, data.family_group_id)
        end_date = _calculate_end_date(data.start_date, data.duration_value, data.duration_unit)
        profit = _calculate_profit(
            data.principal_amount, data.interest_rate,
            data.interest_period, data.duration_value, data.duration_unit,
        )
        projected_total = data.principal_amount + profit

        investment = SimpleInvestment(
            family_group_id=data.family_group_id,
            user_id=user_id,
            name=data.name,
            investment_type=data.investment_type,
            principal_amount=data.principal_amount,
            interest_rate=data.interest_rate,
            interest_period=data.interest_period,
            start_date=data.start_date,
            duration_value=data.duration_value,
            duration_unit=data.duration_unit,
            end_date=end_date,
            projected_profit=profit,
            projected_total=projected_total,
            notes=data.notes,
        )
        self._session.add(investment)
        await self._session.commit()
        await self._session.refresh(investment)
        return SimpleInvestmentResponse.model_validate(investment)

    async def list_investments(
        self, user_id: uuid.UUID, family_group_id: uuid.UUID
    ) -> List[SimpleInvestmentResponse]:
        await require_family_member(self._session, user_id, family_group_id)
        result = await self._session.execute(
            select(SimpleInvestment)
            .where(SimpleInvestment.family_group_id == family_group_id)
            .order_by(SimpleInvestment.created_at.desc())
        )
        return [SimpleInvestmentResponse.model_validate(inv) for inv in result.scalars().all()]

    async def get_investment(
        self, user_id: uuid.UUID, investment_id: uuid.UUID
    ) -> SimpleInvestmentResponse:
        investment = await self._session.get(SimpleInvestment, investment_id)
        if not investment:
            raise NotFoundError(f"SimpleInvestment {investment_id} not found")
        await require_family_member(self._session, user_id, investment.family_group_id)
        return SimpleInvestmentResponse.model_validate(investment)

    async def update_investment(
        self, user_id: uuid.UUID, investment_id: uuid.UUID, data: SimpleInvestmentUpdate
    ) -> SimpleInvestmentResponse:
        investment = await self._session.get(SimpleInvestment, investment_id)
        if not investment:
            raise NotFoundError(f"SimpleInvestment {investment_id} not found")
        await require_family_member(self._session, user_id, investment.family_group_id)

        update_dict = data.model_dump(exclude_none=True)
        for field, value in update_dict.items():
            setattr(investment, field, value)

        investment.end_date = _calculate_end_date(
            investment.start_date, investment.duration_value, investment.duration_unit
        )
        investment.projected_profit = _calculate_profit(
            investment.principal_amount, investment.interest_rate,
            investment.interest_period, investment.duration_value, investment.duration_unit,
        )
        investment.projected_total = investment.principal_amount + investment.projected_profit

        await self._session.commit()
        await self._session.refresh(investment)
        return SimpleInvestmentResponse.model_validate(investment)

    async def delete_investment(self, user_id: uuid.UUID, investment_id: uuid.UUID) -> None:
        investment = await self._session.get(SimpleInvestment, investment_id)
        if not investment:
            raise NotFoundError(f"SimpleInvestment {investment_id} not found")
        await require_family_member(self._session, user_id, investment.family_group_id)
        await self._session.delete(investment)
        await self._session.commit()

    async def get_summary(
        self, user_id: uuid.UUID, family_group_id: uuid.UUID
    ) -> InvestmentSummaryResponse:
        await require_family_member(self._session, user_id, family_group_id)
        investments = await self._session.execute(
            select(SimpleInvestment)
            .where(SimpleInvestment.family_group_id == family_group_id)
            .order_by(SimpleInvestment.created_at.desc())
        )
        total_principal = Decimal("0")
        total_profit = Decimal("0")
        total_value = Decimal("0")
        responses = []
        for inv in investments.scalars().all():
            resp = SimpleInvestmentResponse.model_validate(inv)
            responses.append(resp)
            total_principal += inv.principal_amount
            total_profit += (inv.projected_profit or Decimal("0"))
            total_value += (inv.projected_total or inv.principal_amount)

        return InvestmentSummaryResponse(
            total_principal=total_principal,
            total_projected_profit=total_profit,
            total_projected_value=total_value,
            investments=responses,
        )
