from pydantic import BaseModel, computed_field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
import uuid
from app.models.account import AccountType


class AccountCreate(BaseModel):
    name: str
    account_type: AccountType
    currency: str = "PLN"
    color: Optional[str] = None
    icon: Optional[str] = None
    initial_balance: Decimal = Decimal("0.00")
    opening_date: Optional[date] = None
    is_joint: bool = False
    is_visible_to_family: bool = False
    share_transactions_with_family: bool = False
    # Credit card
    credit_limit: Optional[Decimal] = None
    statement_day: Optional[int] = None
    payment_due_day: Optional[int] = None


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    is_joint: Optional[bool] = None
    is_visible_to_family: Optional[bool] = None
    share_transactions_with_family: Optional[bool] = None
    credit_limit: Optional[Decimal] = None
    statement_day: Optional[int] = None
    payment_due_day: Optional[int] = None


class AccountResponse(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    account_type: AccountType
    currency: str
    color: Optional[str] = None
    icon: Optional[str] = None
    initial_balance: Decimal
    current_balance: Decimal
    opening_date: Optional[date] = None
    is_joint: bool
    is_visible_to_family: bool
    share_transactions_with_family: bool
    is_active: bool
    credit_limit: Optional[Decimal] = None
    statement_day: Optional[int] = None
    payment_due_day: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}

    @computed_field
    @property
    def balance(self) -> Decimal:
        """Alias dla frontendu oczekującego pola 'balance'."""
        return self.current_balance


class BalanceCorrectionRequest(BaseModel):
    actual_balance: Decimal
    note: Optional[str] = None


class AddJointOwnerRequest(BaseModel):
    user_id: uuid.UUID
    notify_on_transaction: bool = True
