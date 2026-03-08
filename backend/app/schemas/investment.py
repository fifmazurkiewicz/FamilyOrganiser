from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
import uuid
from app.models.investment import InvestmentType, BondType


class InvestmentCreate(BaseModel):
    investment_type: InvestmentType
    name: str
    ticker: Optional[str] = None
    quantity: Optional[Decimal] = None
    purchase_price: Optional[Decimal] = None
    current_price: Optional[Decimal] = None
    currency: str = "PLN"
    purchase_date: Optional[date] = None
    notes: Optional[str] = None
    is_shared: bool = False
    # Real estate
    address: Optional[str] = None
    rental_income_monthly: Optional[Decimal] = None
    # Bank deposit
    interest_rate: Optional[Decimal] = None
    maturity_date: Optional[date] = None
    bank_name: Optional[str] = None


class InvestmentUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[Decimal] = None
    current_price: Optional[Decimal] = None
    notes: Optional[str] = None
    is_shared: Optional[bool] = None
    rental_income_monthly: Optional[Decimal] = None


class InvestmentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    investment_type: InvestmentType
    name: str
    ticker: Optional[str] = None
    quantity: Optional[Decimal] = None
    purchase_price: Optional[Decimal] = None
    current_price: Optional[Decimal] = None
    currency: str
    purchase_date: Optional[date] = None
    is_shared: bool
    total_value: Optional[Decimal] = None
    roi_percent: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PolishBondCreate(BaseModel):
    bond_type: BondType
    series: str
    quantity: int
    purchase_date: date
    first_period_rate: Decimal
    notes: Optional[str] = None


class PolishBondResponse(BaseModel):
    id: uuid.UUID
    bond_type: BondType
    series: str
    quantity: int
    purchase_date: date
    maturity_date: date
    first_period_rate: Decimal
    current_value: Decimal
    nominal_value: Decimal
    accrued_interest: Decimal
    is_active: bool
    notes: Optional[str] = None

    model_config = {"from_attributes": True}
