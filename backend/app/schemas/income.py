from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
import uuid
from app.models.income import IncomeCategory


class IncomeTemplateCreate(BaseModel):
    account_id: uuid.UUID
    name: str
    base_amount: Decimal
    currency: str = "PLN"
    category: IncomeCategory = IncomeCategory.SALARY
    day_of_month: int


class IncomeTemplateResponse(BaseModel):
    id: uuid.UUID
    account_id: uuid.UUID
    name: str
    base_amount: Decimal
    currency: str
    category: IncomeCategory
    day_of_month: int
    is_active: bool

    model_config = {"from_attributes": True}


class IncomeCreate(BaseModel):
    account_id: uuid.UUID
    template_id: Optional[uuid.UUID] = None
    name: str
    amount: Decimal
    base_amount: Optional[Decimal] = None
    currency: str = "PLN"
    category: IncomeCategory = IncomeCategory.SALARY
    income_date: date
    is_skipped: bool = False
    description: Optional[str] = None


class IncomeUpdate(BaseModel):
    account_id: Optional[uuid.UUID] = None
    name: Optional[str] = None
    amount: Optional[Decimal] = None
    category: Optional[IncomeCategory] = None
    income_date: Optional[date] = None
    description: Optional[str] = None
    is_skipped: Optional[bool] = None


class IncomeResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    account_id: uuid.UUID
    template_id: Optional[uuid.UUID] = None
    name: str
    amount: Decimal
    base_amount: Optional[Decimal] = None
    currency: str
    category: IncomeCategory
    income_date: date
    is_modified: bool
    is_skipped: bool
    description: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
