from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
import uuid
from app.models.simple_investment import SimpleInvestmentType, InterestPeriod, DurationUnit


class SimpleInvestmentCreate(BaseModel):
    family_group_id: uuid.UUID
    name: str
    investment_type: SimpleInvestmentType
    principal_amount: Decimal
    interest_rate: Decimal
    interest_period: InterestPeriod = InterestPeriod.YEARLY
    start_date: date
    duration_value: int
    duration_unit: DurationUnit = DurationUnit.MONTHS
    notes: Optional[str] = None


class SimpleInvestmentUpdate(BaseModel):
    name: Optional[str] = None
    principal_amount: Optional[Decimal] = None
    interest_rate: Optional[Decimal] = None
    interest_period: Optional[InterestPeriod] = None
    start_date: Optional[date] = None
    duration_value: Optional[int] = None
    duration_unit: Optional[DurationUnit] = None
    notes: Optional[str] = None


class SimpleInvestmentResponse(BaseModel):
    id: uuid.UUID
    family_group_id: uuid.UUID
    user_id: uuid.UUID
    name: str
    investment_type: SimpleInvestmentType
    principal_amount: Decimal
    interest_rate: Decimal
    interest_period: InterestPeriod
    start_date: date
    duration_value: int
    duration_unit: DurationUnit
    end_date: Optional[date] = None
    projected_profit: Optional[Decimal] = None
    projected_total: Optional[Decimal] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class InvestmentSummaryResponse(BaseModel):
    total_principal: Decimal
    total_projected_profit: Decimal
    total_projected_value: Decimal
    investments: list[SimpleInvestmentResponse]