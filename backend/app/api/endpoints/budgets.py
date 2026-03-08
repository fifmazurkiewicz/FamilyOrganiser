import uuid
from typing import Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.db.base import get_db
from app.models.user import User
from app.models.budget import Budget, BudgetCategory
from app.models.transaction import Transaction, TransactionType
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse, BudgetCategoryResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    payload: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    budget = Budget(
        user_id=current_user.id,
        family_group_id=payload.family_group_id,
        name=payload.name,
        scope=payload.scope,
        year=payload.year,
        month=payload.month,
        alert_threshold_percent=payload.alert_threshold_percent,
    )
    db.add(budget)
    await db.flush()

    for cat in payload.categories:
        bc = BudgetCategory(
            budget_id=budget.id,
            category_id=cat.category_id,
            planned_amount=cat.planned_amount,
            currency=cat.currency,
        )
        db.add(bc)

    await db.commit()
    await db.refresh(budget)
    return await _enrich_budget(budget, current_user.id, db)


@router.get("/", response_model=list[BudgetResponse])
async def list_budgets(
    year: Optional[int] = None,
    month: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conditions = [Budget.user_id == current_user.id]
    if year:
        conditions.append(Budget.year == year)
    if month:
        conditions.append(Budget.month == month)

    result = await db.execute(select(Budget).where(and_(*conditions)))
    budgets = result.scalars().all()
    return [await _enrich_budget(b, current_user.id, db) for b in budgets]


@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(
    budget_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Budget).where(Budget.id == budget_id, Budget.user_id == current_user.id)
    )
    budget = result.scalar_one_or_none()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return await _enrich_budget(budget, current_user.id, db)


@router.patch("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: uuid.UUID,
    payload: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Budget).where(Budget.id == budget_id, Budget.user_id == current_user.id)
    )
    budget = result.scalar_one_or_none()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    if payload.name is not None:
        budget.name = payload.name
    if payload.alert_threshold_percent is not None:
        budget.alert_threshold_percent = payload.alert_threshold_percent

    await db.commit()
    return await _enrich_budget(budget, current_user.id, db)


@router.delete("/{budget_id}")
async def delete_budget(
    budget_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Budget).where(Budget.id == budget_id, Budget.user_id == current_user.id)
    )
    budget = result.scalar_one_or_none()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    await db.delete(budget)
    await db.commit()
    return {"message": "Budget deleted"}


async def _enrich_budget(budget: Budget, user_id: uuid.UUID, db: AsyncSession) -> BudgetResponse:
    """Add actual spending to each budget category."""
    cats_result = await db.execute(
        select(BudgetCategory).where(BudgetCategory.budget_id == budget.id)
    )
    cats = cats_result.scalars().all()

    enriched_cats = []
    for bc in cats:
        # Sum actual expenses for category in the period
        conditions = [
            Transaction.user_id == user_id,
            Transaction.category_id == bc.category_id,
            Transaction.transaction_type == TransactionType.EXPENSE,
        ]
        if budget.month:
            from sqlalchemy import extract
            conditions.append(extract("year", Transaction.transaction_date) == budget.year)
            conditions.append(extract("month", Transaction.transaction_date) == budget.month)
        else:
            from sqlalchemy import extract
            conditions.append(extract("year", Transaction.transaction_date) == budget.year)

        result = await db.execute(
            select(func.sum(Transaction.amount)).where(and_(*conditions))
        )
        actual = result.scalar() or Decimal("0.00")

        enriched_cats.append(BudgetCategoryResponse(
            id=bc.id,
            category_id=bc.category_id,
            planned_amount=bc.planned_amount,
            currency=bc.currency,
            actual_amount=actual,
        ))

    return BudgetResponse(
        id=budget.id,
        user_id=budget.user_id,
        name=budget.name,
        scope=budget.scope,
        year=budget.year,
        month=budget.month,
        alert_threshold_percent=budget.alert_threshold_percent,
        categories=enriched_cats,
        created_at=budget.created_at,
    )
