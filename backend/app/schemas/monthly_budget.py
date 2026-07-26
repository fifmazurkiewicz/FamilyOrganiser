from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import uuid
from app.models.monthly_budget import BudgetEntryType


class BudgetEntryCreate(BaseModel):
    entry_type: BudgetEntryType
    name: str
    amount: Decimal
    is_recurring: bool = False


class BudgetEntryResponse(BaseModel):
    id: uuid.UUID
    budget_id: uuid.UUID
    entry_type: BudgetEntryType
    name: str
    amount: Decimal
    is_recurring: bool
    created_by: uuid.UUID

    model_config = {"from_attributes": True}


class MonthlyBudgetCreate(BaseModel):
    family_group_id: uuid.UUID
    year: int
    month: int


class MonthlyBudgetResponse(BaseModel):
    id: uuid.UUID
    family_group_id: uuid.UUID
    year: int
    month: int
    created_at: datetime
    entries: list[BudgetEntryResponse] = []

    model_config = {"from_attributes": True}


class BudgetSummaryResponse(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    remaining: Decimal