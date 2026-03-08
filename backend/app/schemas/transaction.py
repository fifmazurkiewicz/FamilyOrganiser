from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
import uuid
from app.models.transaction import TransactionType, TransactionScope, RecurringFrequency


class TransactionCategoryCreate(BaseModel):
    name: str
    parent_id: Optional[uuid.UUID] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class TransactionCategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    parent_id: Optional[uuid.UUID] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_system: bool

    model_config = {"from_attributes": True}


class TagCreate(BaseModel):
    name: str


class TagResponse(BaseModel):
    id: uuid.UUID
    name: str

    model_config = {"from_attributes": True}


class TransactionCreate(BaseModel):
    account_id: uuid.UUID
    category_id: Optional[uuid.UUID] = None
    family_group_id: Optional[uuid.UUID] = None
    transaction_type: TransactionType
    scope: TransactionScope = TransactionScope.PERSONAL
    amount: Decimal
    currency: str = "PLN"
    transaction_date: date
    description: Optional[str] = None
    tag_ids: List[uuid.UUID] = []
    recurring_id: Optional[uuid.UUID] = None


class TransactionUpdate(BaseModel):
    category_id: Optional[uuid.UUID] = None
    scope: Optional[TransactionScope] = None
    amount: Optional[Decimal] = None
    transaction_date: Optional[date] = None
    description: Optional[str] = None
    tag_ids: Optional[List[uuid.UUID]] = None


class TransactionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    account_id: uuid.UUID
    category_id: Optional[uuid.UUID] = None
    family_group_id: Optional[uuid.UUID] = None
    transaction_type: TransactionType
    scope: TransactionScope
    amount: Decimal
    currency: str
    amount_pln: Optional[Decimal] = None
    exchange_rate: Optional[Decimal] = None
    transaction_date: date
    description: Optional[str] = None
    is_recurring: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class RecurringTransactionCreate(BaseModel):
    account_id: uuid.UUID
    category_id: Optional[uuid.UUID] = None
    name: str
    amount: Decimal
    currency: str = "PLN"
    transaction_type: TransactionType
    frequency: RecurringFrequency = RecurringFrequency.MONTHLY
    day_of_month: int = 1
    reminder_days_before: int = 3
    total_occurrences: Optional[int] = None
    start_date: date
    end_date: Optional[date] = None
    description: Optional[str] = None


class RecurringTransactionResponse(BaseModel):
    id: uuid.UUID
    name: str
    amount: Decimal
    currency: str
    transaction_type: TransactionType
    frequency: RecurringFrequency
    day_of_month: int
    reminder_days_before: int
    is_active: bool
    start_date: date
    end_date: Optional[date] = None

    model_config = {"from_attributes": True}
