import uuid
from datetime import date
from typing import Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db.base import get_db
from app.models.user import User
from app.models.account import Account, JointAccountOwner
from app.models.transaction import Transaction, TransactionCategory, TransactionTag, RecurringTransaction
from app.schemas.transaction import (
    TransactionCreate, TransactionUpdate, TransactionResponse,
    TransactionCategoryCreate, TransactionCategoryResponse,
    TagCreate, TagResponse,
    RecurringTransactionCreate, RecurringTransactionResponse,
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/categories", response_model=list[TransactionCategoryResponse])
async def list_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TransactionCategory).where(
            (TransactionCategory.user_id == current_user.id) |
            (TransactionCategory.is_system == True)
        )
    )
    return result.scalars().all()


@router.post("/categories", response_model=TransactionCategoryResponse, status_code=201)
async def create_category(
    payload: TransactionCategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    category = TransactionCategory(
        user_id=current_user.id,
        name=payload.name,
        parent_id=payload.parent_id,
        icon=payload.icon,
        color=payload.color,
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@router.get("/tags", response_model=list[TagResponse])
async def list_tags(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TransactionTag).where(TransactionTag.user_id == current_user.id)
    )
    return result.scalars().all()


@router.post("/tags", response_model=TagResponse, status_code=201)
async def create_tag(
    payload: TagCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tag = TransactionTag(user_id=current_user.id, name=payload.name)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


async def _resolve_amount_pln(amount: Decimal, currency: str, db: AsyncSession) -> tuple[Decimal, Decimal | None]:
    if currency == "PLN":
        return amount, None
    from app.models.exchange_rate import ExchangeRate
    from sqlalchemy import desc
    result = await db.execute(
        select(ExchangeRate).where(ExchangeRate.currency == currency).order_by(desc(ExchangeRate.rate_date)).limit(1)
    )
    rate = result.scalar_one_or_none()
    if rate:
        return amount * rate.rate_to_pln, rate.rate_to_pln
    return amount, None


@router.post("/", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    payload: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Validate account access
    acc_result = await db.execute(select(Account).where(Account.id == payload.account_id))
    account = acc_result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if account.owner_id != current_user.id:
        joint = await db.execute(
            select(JointAccountOwner).where(
                JointAccountOwner.account_id == payload.account_id,
                JointAccountOwner.user_id == current_user.id,
            )
        )
        if not joint.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Access denied to this account")

    amount_pln, exchange_rate = await _resolve_amount_pln(payload.amount, payload.currency, db)

    tx = Transaction(
        user_id=current_user.id,
        account_id=payload.account_id,
        category_id=payload.category_id,
        family_group_id=payload.family_group_id,
        transaction_type=payload.transaction_type,
        scope=payload.scope,
        amount=payload.amount,
        currency=payload.currency,
        amount_pln=amount_pln,
        exchange_rate=exchange_rate,
        transaction_date=payload.transaction_date,
        description=payload.description,
        recurring_id=payload.recurring_id,
        is_recurring=payload.recurring_id is not None,
    )
    db.add(tx)

    # Update account balance
    from app.models.transaction import TransactionType
    if payload.transaction_type == TransactionType.EXPENSE:
        account.current_balance -= payload.amount
    else:
        account.current_balance += payload.amount

    await db.flush()

    # Attach tags
    for tag_id in payload.tag_ids:
        tag_result = await db.execute(
            select(TransactionTag).where(
                TransactionTag.id == tag_id,
                TransactionTag.user_id == current_user.id,
            )
        )
        tag = tag_result.scalar_one_or_none()
        if tag:
            tx.tags.append(tag)

    await db.commit()
    await db.refresh(tx)
    return tx


@router.get("/", response_model=list[TransactionResponse])
async def list_transactions(
    account_id: Optional[uuid.UUID] = None,
    category_id: Optional[uuid.UUID] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(default=50, le=500),
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conditions = [Transaction.user_id == current_user.id]
    if account_id:
        conditions.append(Transaction.account_id == account_id)
    if category_id:
        conditions.append(Transaction.category_id == category_id)
    if start_date:
        conditions.append(Transaction.transaction_date >= start_date)
    if end_date:
        conditions.append(Transaction.transaction_date <= end_date)

    result = await db.execute(
        select(Transaction).where(and_(*conditions))
        .order_by(Transaction.transaction_date.desc())
        .offset(offset).limit(limit)
    )
    return result.scalars().all()


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id,
        )
    )
    tx = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: uuid.UUID,
    payload: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id,
        )
    )
    tx = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Adjust balance if amount changes
    if payload.amount is not None and payload.amount != tx.amount:
        acc_result = await db.execute(select(Account).where(Account.id == tx.account_id))
        account = acc_result.scalar_one()
        from app.models.transaction import TransactionType
        if tx.transaction_type == TransactionType.EXPENSE:
            account.current_balance += tx.amount  # reverse old
            account.current_balance -= payload.amount  # apply new
        else:
            account.current_balance -= tx.amount
            account.current_balance += payload.amount
        tx.amount = payload.amount

    if payload.category_id is not None:
        tx.category_id = payload.category_id
    if payload.scope is not None:
        tx.scope = payload.scope
    if payload.transaction_date is not None:
        tx.transaction_date = payload.transaction_date
    if payload.description is not None:
        tx.description = payload.description

    await db.commit()
    await db.refresh(tx)
    return tx


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id,
        )
    )
    tx = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Reverse balance
    acc_result = await db.execute(select(Account).where(Account.id == tx.account_id))
    account = acc_result.scalar_one_or_none()
    if account:
        from app.models.transaction import TransactionType
        if tx.transaction_type == TransactionType.EXPENSE:
            account.current_balance += tx.amount
        else:
            account.current_balance -= tx.amount

    await db.delete(tx)
    await db.commit()
    return {"message": "Transaction deleted"}


# Recurring transactions
@router.post("/recurring", response_model=RecurringTransactionResponse, status_code=201)
async def create_recurring(
    payload: RecurringTransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    recurring = RecurringTransaction(
        user_id=current_user.id,
        account_id=payload.account_id,
        category_id=payload.category_id,
        name=payload.name,
        amount=payload.amount,
        currency=payload.currency,
        transaction_type=payload.transaction_type,
        day_of_month=payload.day_of_month,
        reminder_days_before=payload.reminder_days_before,
        total_occurrences=payload.total_occurrences,
        start_date=payload.start_date,
        end_date=payload.end_date,
        description=payload.description,
    )
    db.add(recurring)
    await db.commit()
    await db.refresh(recurring)
    return recurring


@router.get("/recurring/list", response_model=list[RecurringTransactionResponse])
async def list_recurring(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RecurringTransaction).where(
            RecurringTransaction.user_id == current_user.id,
            RecurringTransaction.is_active == True,
        )
    )
    return result.scalars().all()
