from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import uuid
from app.models.budget import BudgetScope


class BudgetCategoryCreate(BaseModel):
    category_id: uuid.UUID
    planned_amount: Decimal
    currency: str = "PLN"


class BudgetCategoryResponse(BaseModel):
    id: uuid.UUID
    category_id: uuid.UUID
    planned_amount: Decimal
    currency: str
    actual_amount: Decimal = Decimal("0.00")

    model_config = {"from_attributes": True}


class BudgetCreate(BaseModel):
    name: str
    scope: BudgetScope = BudgetScope.PERSONAL
    year: int
    month: Optional[int] = None  # None = annual
    family_group_id: Optional[uuid.UUID] = None
    alert_threshold_percent: int = 80
    categories: List[BudgetCategoryCreate] = []


class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    alert_threshold_percent: Optional[int] = None


class BudgetResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    scope: BudgetScope
    year: int
    month: Optional[int] = None
    alert_threshold_percent: int
    categories: List[BudgetCategoryResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}
