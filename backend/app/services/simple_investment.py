import uuid
from datetime import date
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.simple_investment import (
    SimpleInvestment, InterestPeriod, DurationUnit,
)
from app.repositories.simple_investment import SimpleInvestmentRepository
from app.schemas.simple_investment import (
    SimpleInvestmentCreate, SimpleInvestmentUpdate,
    SimpleInvestmentResponse, InvestmentSummaryResponse,
)


DURATION_TO_MONTHS = {
    DurationUnit.MONTHS: 1,
    DurationUnit.QUARTERS: 3,
    DurationUnit.YEARS: 12,
}

PERIOD_TO_MONTHS = {
    InterestPeriod.MONTHLY: 1,
    InterestPeriod.QUARTERLY: 3,
    InterestPeriod.YEARLY: 12,
}


def _calculate_end_date(start_date: date, duration_value: int, duration_unit: DurationUnit) -> date:
    months_to_add = duration_value * DURATION_TO_MONTHS[duration_unit]
    return start_date + relativedelta(months=months_to_add)


def _calculate_profit(
    principal: Decimal,
    rate: Decimal,
    interest_period: InterestPeriod,
    duration_value: int,
    duration_unit: DurationUnit,
) -> Decimal:
    """Simple interest: profit = principal * rate * (duration in years)."""
    total_months = Decimal(duration_value * DURATION_TO_MONTHS[duration_unit])
    period_months = Decimal(PERIOD_TO_MONTHS[interest_period])
    years_fraction = total_months / Decimal("12")
    return principal * rate * years_fraction


def _calculate_profit_compound(
    principal: Decimal,
    rate: Decimal,
    interest_period: InterestPeriod,
    duration_value: int,
    duration_unit: DurationUnit,
) -> Decimal:
    """Compound interest."""
    total_months = duration_value * DURATION_TO_MONTHS[duration_unit]
    period_months = PERIOD_TO_MONTHS[interest_period]
    periods = total_months // period_months
    period_rate = rate / Decimal(PERIOD_TO_MONTHS[InterestPeriod.YEARLY] / period_months)
    future_value = principal * (1 + period_rate) ** Decimal(periods)
    return future_value - principal


class SimpleInvestmentService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = SimpleInvestmentRepository(db)

    async def list_investments(
        self, family_group_id: uuid.UUID
    ) -> List[SimpleInvestmentResponse]:
        investments = await self.repo.list_for_family(family_group_id)
        return [SimpleInvestmentResponse.model_validate(inv) for inv in investments]

    async def create_investment(
        self, user_id: uuid.UUID, data: SimpleInvestmentCreate
    ) -> SimpleInvestmentResponse:
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
        await self.repo.add(investment)
        await self.repo.commit()
        return SimpleInvestmentResponse.model_validate(investment)

    async def get_investment(self, investment_id: uuid.UUID) -> SimpleInvestmentResponse:
        investment = await self.repo.get_or_raise(investment_id)
        return SimpleInvestmentResponse.model_validate(investment)

    async def update_investment(
        self, investment_id: uuid.UUID, data: SimpleInvestmentUpdate
    ) -> SimpleInvestmentResponse:
        investment = await self.repo.get_or_raise(investment_id)

        update_dict = data.model_dump(exclude_none=True)
        for field, value in update_dict.items():
            setattr(investment, field, value)

        # Recalculate derived fields
        investment.end_date = _calculate_end_date(
            investment.start_date, investment.duration_value, investment.duration_unit
        )
        investment.projected_profit = _calculate_profit(
            investment.principal_amount, investment.interest_rate,
            investment.interest_period, investment.duration_value, investment.duration_unit,
        )
        investment.projected_total = investment.principal_amount + investment.projected_profit

        await self.repo.commit()
        return SimpleInvestmentResponse.model_validate(investment)

    async def delete_investment(self, investment_id: uuid.UUID) -> None:
        investment = await self.repo.get_or_raise(investment_id)
        await self.repo.delete(investment)
        await self.repo.commit()

    async def get_summary(
        self, family_group_id: uuid.UUID
    ) -> InvestmentSummaryResponse:
        investments = await self.repo.list_for_family(family_group_id)
        total_principal = Decimal("0")
        total_profit = Decimal("0")
        total_value = Decimal("0")
        responses = []
        for inv in investments:
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