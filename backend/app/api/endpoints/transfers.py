import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from typing import Optional

from app.db.base import get_db
from app.models.user import User
from app.models.account import Account
from app.models.savings import SavingsGoal
from app.models.transfer import Transfer, TransferType
from app.api.deps import get_current_user

router = APIRouter(prefix="/transfers", tags=["transfers"])


class TransferCreate(BaseModel):
    transfer_type: TransferType
    from_account_id: Optional[uuid.UUID] = None
    to_account_id: Optional[uuid.UUID] = None
    from_goal_id: Optional[uuid.UUID] = None
    to_goal_id: Optional[uuid.UUID] = None
    amount: Decimal
    currency: str = "PLN"
    transfer_date: date
    description: Optional[str] = None


@router.post("/", status_code=201)
async def create_transfer(
    payload: TransferCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Validate and process transfer
    transfer = Transfer(
        user_id=current_user.id,
        transfer_type=payload.transfer_type,
        from_account_id=payload.from_account_id,
        to_account_id=payload.to_account_id,
        from_goal_id=payload.from_goal_id,
        to_goal_id=payload.to_goal_id,
        amount=payload.amount,
        currency=payload.currency,
        transfer_date=payload.transfer_date,
        description=payload.description,
    )
    db.add(transfer)

    # Update balances based on transfer type
    if payload.transfer_type == TransferType.ACCOUNT_TO_ACCOUNT:
        if payload.from_account_id:
            result = await db.execute(select(Account).where(Account.id == payload.from_account_id))
            from_acc = result.scalar_one_or_none()
            if from_acc:
                from_acc.current_balance -= payload.amount
        if payload.to_account_id:
            result = await db.execute(select(Account).where(Account.id == payload.to_account_id))
            to_acc = result.scalar_one_or_none()
            if to_acc:
                to_acc.current_balance += payload.amount

    elif payload.transfer_type == TransferType.ACCOUNT_TO_GOAL:
        if payload.from_account_id:
            result = await db.execute(select(Account).where(Account.id == payload.from_account_id))
            acc = result.scalar_one_or_none()
            if acc:
                acc.current_balance -= payload.amount
        if payload.to_goal_id:
            result = await db.execute(select(SavingsGoal).where(SavingsGoal.id == payload.to_goal_id))
            goal = result.scalar_one_or_none()
            if goal:
                goal.current_amount += payload.amount

    elif payload.transfer_type == TransferType.GOAL_TO_ACCOUNT:
        if payload.from_goal_id:
            result = await db.execute(select(SavingsGoal).where(SavingsGoal.id == payload.from_goal_id))
            goal = result.scalar_one_or_none()
            if goal:
                goal.current_amount -= payload.amount
        if payload.to_account_id:
            result = await db.execute(select(Account).where(Account.id == payload.to_account_id))
            acc = result.scalar_one_or_none()
            if acc:
                acc.current_balance += payload.amount

    elif payload.transfer_type == TransferType.GOAL_TO_GOAL:
        if payload.from_goal_id:
            result = await db.execute(select(SavingsGoal).where(SavingsGoal.id == payload.from_goal_id))
            from_goal = result.scalar_one_or_none()
            if from_goal:
                from_goal.current_amount -= payload.amount
        if payload.to_goal_id:
            result = await db.execute(select(SavingsGoal).where(SavingsGoal.id == payload.to_goal_id))
            to_goal = result.scalar_one_or_none()
            if to_goal:
                to_goal.current_amount += payload.amount

    await db.commit()
    return {"message": "Transfer completed", "transfer_id": str(transfer.id)}


@router.get("/")
async def list_transfers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Transfer).where(Transfer.user_id == current_user.id)
        .order_by(Transfer.transfer_date.desc())
    )
    transfers = result.scalars().all()
    return [
        {
            "id": str(t.id),
            "transfer_type": t.transfer_type.value,
            "from_account_id": str(t.from_account_id) if t.from_account_id else None,
            "to_account_id": str(t.to_account_id) if t.to_account_id else None,
            "from_goal_id": str(t.from_goal_id) if t.from_goal_id else None,
            "to_goal_id": str(t.to_goal_id) if t.to_goal_id else None,
            "amount": str(t.amount),
            "currency": t.currency,
            "transfer_date": str(t.transfer_date),
            "description": t.description,
            "created_at": t.created_at.isoformat(),
        }
        for t in transfers
    ]
