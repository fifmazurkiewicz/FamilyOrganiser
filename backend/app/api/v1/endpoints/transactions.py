import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.schemas.transaction import (
    RecurringTransactionCreate,
    RecurringTransactionResponse,
    TagCreate,
    TagResponse,
    TransactionCategoryCreate,
    TransactionCategoryResponse,
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
)
from app.services.transaction import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/categories", response_model=list[TransactionCategoryResponse])
async def list_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = TransactionService(db)
    return await svc.list_categories(current_user.id)


@router.post("/categories", response_model=TransactionCategoryResponse, status_code=201)
async def create_category(
    payload: TransactionCategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = TransactionService(db)
    return await svc.create_category(
        current_user.id, payload.name, payload.parent_id, payload.icon, payload.color
    )


@router.get("/tags", response_model=list[TagResponse])
async def list_tags(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = TransactionService(db)
    return await svc.list_tags(current_user.id)


@router.post("/tags", response_model=TagResponse, status_code=201)
async def create_tag(
    payload: TagCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = TransactionService(db)
    return await svc.create_tag(current_user.id, payload.name)


@router.post("/", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    payload: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = TransactionService(db)
    return await svc.create(current_user.id, **payload.model_dump())


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
    svc = TransactionService(db)
    return await svc.list(
        current_user.id,
        account_id=account_id,
        category_id=category_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = TransactionService(db)
    return await svc.get_owned(transaction_id, current_user.id)


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: uuid.UUID,
    payload: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = TransactionService(db)
    tx = await svc.get_owned(transaction_id, current_user.id)
    return await svc.update(tx, **payload.model_dump(exclude_none=True))


@router.delete("/{transaction_id}", status_code=204)
async def delete_transaction(
    transaction_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = TransactionService(db)
    tx = await svc.get_owned(transaction_id, current_user.id)
    await svc.delete(tx)


@router.post("/recurring", response_model=RecurringTransactionResponse, status_code=201)
async def create_recurring(
    payload: RecurringTransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = TransactionService(db)
    return await svc.create_recurring(user_id=current_user.id, **payload.model_dump())


@router.get("/recurring/list", response_model=list[RecurringTransactionResponse])
async def list_recurring(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = TransactionService(db)
    return await svc.list_active_recurring(current_user.id)


@router.delete("/recurring/{recurring_id}", status_code=204)
async def deactivate_recurring(
    recurring_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = TransactionService(db)
    await svc.deactivate_recurring(recurring_id, current_user.id)
