from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
import uuid
from app.models.savings import GoalType, GoalVisibility


class SavingsGoalCreate(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    target_amount: Decimal
    currency: str = "PLN"
    goal_type: GoalType = GoalType.PERSONAL
    visibility: GoalVisibility = GoalVisibility.PRIVATE
    target_date: Optional[date] = None
    monthly_contribution: Optional[Decimal] = None
    linked_account_id: Optional[uuid.UUID] = None
    family_group_id: Optional[uuid.UUID] = None
    priority: int = 0


class SavingsGoalUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    target_amount: Optional[Decimal] = None
    target_date: Optional[date] = None
    monthly_contribution: Optional[Decimal] = None
    visibility: Optional[GoalVisibility] = None
    priority: Optional[int] = None


class SavingsGoalResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    target_amount: Decimal
    current_amount: Decimal
    currency: str
    goal_type: GoalType
    visibility: GoalVisibility
    target_date: Optional[date] = None
    monthly_contribution: Optional[Decimal] = None
    is_completed: bool
    is_active: bool
    priority: int
    progress_percent: float = 0.0
    created_at: datetime

    model_config = {"from_attributes": True}


class ContributionCreate(BaseModel):
    amount: Decimal
    source_account_id: Optional[uuid.UUID] = None
    contribution_date: date
    note: Optional[str] = None
    is_withdrawal: bool = False


class ContributionResponse(BaseModel):
    id: uuid.UUID
    goal_id: uuid.UUID
    user_id: uuid.UUID
    amount: Decimal
    currency: str
    contribution_date: date
    note: Optional[str] = None
    is_withdrawal: bool
    created_at: datetime

    model_config = {"from_attributes": True}
