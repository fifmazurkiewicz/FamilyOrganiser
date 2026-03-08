import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db.base import get_db
from app.models.user import User
from app.models.income import Income, IncomeTemplate
from app.schemas.income import (
    IncomeCreate, IncomeUpdate, IncomeResponse,
    IncomeTemplateCreate, IncomeTemplateResponse,
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/income", tags=["income"])


@router.post("/templates", response_model=IncomeTemplateResponse, status_code=201)
async def create_template(
    payload: IncomeTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    template = IncomeTemplate(user_id=current_user.id, **payload.model_dump())
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


@router.get("/templates", response_model=list[IncomeTemplateResponse])
async def list_templates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(IncomeTemplate).where(
            IncomeTemplate.user_id == current_user.id,
            IncomeTemplate.is_active == True,
        )
    )
    return result.scalars().all()


@router.post("/", response_model=IncomeResponse, status_code=201)
async def create_income(
    payload: IncomeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    is_modified = (
        payload.base_amount is not None and payload.amount != payload.base_amount
    )
    income = Income(
        user_id=current_user.id,
        account_id=payload.account_id,
        template_id=payload.template_id,
        name=payload.name,
        amount=payload.amount,
        base_amount=payload.base_amount,
        currency=payload.currency,
        category=payload.category,
        income_date=payload.income_date,
        is_modified=is_modified,
        is_skipped=payload.is_skipped,
        description=payload.description,
    )
    db.add(income)

    # Update account balance if not skipped
    if not payload.is_skipped:
        from app.models.account import Account
        acc_result = await db.execute(select(Account).where(Account.id == payload.account_id))
        account = acc_result.scalar_one_or_none()
        if account:
            account.current_balance += payload.amount

    await db.commit()
    await db.refresh(income)
    return income


@router.get("/", response_model=list[IncomeResponse])
async def list_incomes(
    year: Optional[int] = None,
    month: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conditions = [Income.user_id == current_user.id]
    if year:
        from sqlalchemy import extract
        conditions.append(extract("year", Income.income_date) == year)
    if month:
        from sqlalchemy import extract
        conditions.append(extract("month", Income.income_date) == month)

    result = await db.execute(
        select(Income).where(and_(*conditions)).order_by(Income.income_date.desc())
    )
    return result.scalars().all()


@router.patch("/{income_id}", response_model=IncomeResponse)
async def update_income(
    income_id: uuid.UUID,
    payload: IncomeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Income).where(Income.id == income_id, Income.user_id == current_user.id)
    )
    income = result.scalar_one_or_none()
    if not income:
        raise HTTPException(status_code=404, detail="Income not found")

    if payload.amount is not None and payload.amount != income.amount:
        from app.models.account import Account
        acc_result = await db.execute(select(Account).where(Account.id == income.account_id))
        account = acc_result.scalar_one_or_none()
        if account and not income.is_skipped:
            account.current_balance -= income.amount
            account.current_balance += payload.amount

        if income.base_amount:
            income.is_modified = payload.amount != income.base_amount
        income.amount = payload.amount

    if payload.description is not None:
        income.description = payload.description
    if payload.is_skipped is not None:
        income.is_skipped = payload.is_skipped

    await db.commit()
    await db.refresh(income)
    return income
