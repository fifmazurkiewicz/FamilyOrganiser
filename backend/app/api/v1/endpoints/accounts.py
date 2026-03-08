import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.schemas.account import (
    AccountCreate,
    AccountResponse,
    AccountUpdate,
    AddJointOwnerRequest,
    BalanceCorrectionRequest,
)
from app.services.account import AccountService

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("/", response_model=AccountResponse, status_code=201)
async def create_account(
    payload: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = AccountService(db)
    return await svc.create(current_user.id, **payload.model_dump())


@router.get("/", response_model=list[AccountResponse])
async def list_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = AccountService(db)
    return await svc.list_all(current_user.id)


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = AccountService(db)
    return await svc.get_accessible(account_id, current_user.id)


@router.patch("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: uuid.UUID,
    payload: AccountUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = AccountService(db)
    account = await svc.require_owner(account_id, current_user.id)
    return await svc.update(account, **payload.model_dump(exclude_none=True))


@router.delete("/{account_id}", status_code=204)
async def delete_account(
    account_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = AccountService(db)
    account = await svc.require_owner(account_id, current_user.id)
    await svc.deactivate(account)


@router.post("/{account_id}/correct-balance")
async def correct_balance(
    account_id: uuid.UUID,
    payload: BalanceCorrectionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = AccountService(db)
    account = await svc.get_accessible(account_id, current_user.id)
    updated = await svc.correct_balance(account, current_user.id, payload.actual_balance, payload.note)
    return {"message": "Balance corrected", "new_balance": str(updated.current_balance)}


@router.post("/{account_id}/joint-owners", status_code=201)
async def add_joint_owner(
    account_id: uuid.UUID,
    payload: AddJointOwnerRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = AccountService(db)
    account = await svc.require_owner(account_id, current_user.id)
    await svc.add_joint_owner(account, payload.user_id, payload.notify_on_transaction)
    return {"message": "Joint owner added"}
