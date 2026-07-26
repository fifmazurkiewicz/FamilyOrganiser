from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
import uuid


class SimpleExpenseCreate(BaseModel):
    family_group_id: uuid.UUID
    amount: Decimal
    description: str
    expense_date: date


class SimpleExpenseResponse(BaseModel):
    id: uuid.UUID
    family_group_id: uuid.UUID
    user_id: uuid.UUID
    amount: Decimal
    description: str
    expense_date: date
    created_at: datetime

    model_config = {"from_attributes": True}