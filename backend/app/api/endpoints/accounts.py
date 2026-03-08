import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal

from app.db.base import get_db
from app.models.user import User
from app.models.account import Account, JointAccountOwner
from app.models.transaction import Transaction
from app.schemas.account import AccountCreate, AccountUpdate, AccountResponse, BalanceCorrectionRequest, AddJointOwnerRequest
from app.api.deps import get_current_user

router = APIRouter(prefix="/accounts", tags=["accounts"])


async def _get_account(account_id: uuid.UUID, user: User, db: AsyncSession) -> Account:
    result = await db.execute(
        select(Account).where(Account.id == account_id)
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Check ownership (own or joint)
    if account.owner_id != user.id:
        joint_result = await db.execute(
            select(JointAccountOwner).where(
                JointAccountOwner.account_id == account_id,
                JointAccountOwner.user_id == user.id,
            )
        )
        if not joint_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Access denied")
    return account


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    payload: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    account = Account(
        owner_id=current_user.id,
        name=payload.name,
        account_type=payload.account_type,
        currency=payload.currency,
        color=payload.color,
        icon=payload.icon,
        initial_balance=payload.initial_balance,
        current_balance=payload.initial_balance,
        opening_date=payload.opening_date,
        is_joint=payload.is_joint,
        is_visible_to_family=payload.is_visible_to_family,
        share_transactions_with_family=payload.share_transactions_with_family,
        credit_limit=payload.credit_limit,
        statement_day=payload.statement_day,
        payment_due_day=payload.payment_due_day,
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


@router.get("/", response_model=list[AccountResponse])
async def list_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Own accounts
    result = await db.execute(
        select(Account).where(Account.owner_id == current_user.id, Account.is_active == True)
    )
    accounts = list(result.scalars().all())

    # Joint accounts where user is co-owner
    joint_result = await db.execute(
        select(JointAccountOwner).where(JointAccountOwner.user_id == current_user.id)
    )
    joint_ownerships = joint_result.scalars().all()
    own_ids = {a.id for a in accounts}
    for jo in joint_ownerships:
        if jo.account_id not in own_ids:
            acc_result = await db.execute(
                select(Account).where(Account.id == jo.account_id, Account.is_active == True)
            )
            acc = acc_result.scalar_one_or_none()
            if acc:
                accounts.append(acc)

    return accounts


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _get_account(account_id, current_user, db)


@router.patch("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: uuid.UUID,
    payload: AccountUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    account = await _get_account(account_id, current_user, db)
    if account.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can update account")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(account, field, value)
    await db.commit()
    await db.refresh(account)
    return account


@router.delete("/{account_id}")
async def delete_account(
    account_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    account = await _get_account(account_id, current_user, db)
    if account.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can delete account")
    if account.is_joint:
        raise HTTPException(
            status_code=400,
            detail="Joint accounts require approval from all owners to delete"
        )
    account.is_active = False
    await db.commit()
    return {"message": "Account deactivated"}


@router.post("/{account_id}/correct-balance")
async def correct_balance(
    account_id: uuid.UUID,
    payload: BalanceCorrectionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    account = await _get_account(account_id, current_user, db)
    old_balance = account.current_balance
    account.current_balance = payload.actual_balance

    # Record correction as a transaction
    from app.models.transaction import Transaction, TransactionType, TransactionScope
    from datetime import date
    diff = payload.actual_balance - old_balance
    if diff != 0:
        correction = Transaction(
            user_id=current_user.id,
            account_id=account_id,
            transaction_type=TransactionType.INCOME if diff > 0 else TransactionType.EXPENSE,
            scope=TransactionScope.PERSONAL,
            amount=abs(diff),
            currency=account.currency,
            transaction_date=date.today(),
            description=f"Korekta salda: {payload.note or ''}",
        )
        db.add(correction)

    await db.commit()
    return {"message": "Balance corrected", "new_balance": str(account.current_balance)}


@router.post("/{account_id}/joint-owners", status_code=status.HTTP_201_CREATED)
async def add_joint_owner(
    account_id: uuid.UUID,
    payload: AddJointOwnerRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    account = await _get_account(account_id, current_user, db)
    if account.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can add joint owners")

    existing = await db.execute(
        select(JointAccountOwner).where(
            JointAccountOwner.account_id == account_id,
            JointAccountOwner.user_id == payload.user_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already a joint owner")

    joint = JointAccountOwner(
        account_id=account_id,
        user_id=payload.user_id,
        notify_on_transaction=payload.notify_on_transaction,
    )
    db.add(joint)
    account.is_joint = True
    await db.commit()
    return {"message": "Joint owner added"}
