import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.services.monthly_budget import MonthlyBudgetService
from app.schemas.monthly_budget import (
    MonthlyBudgetCreate, MonthlyBudgetResponse,
    BudgetEntryCreate, BudgetEntryResponse,
    BudgetSummaryResponse,
)

router = APIRouter(prefix="/monthly-budgets", tags=["Monthly Budgets"])


@router.post("/", response_model=MonthlyBudgetResponse, status_code=201)
async def get_or_create_budget(
    data: MonthlyBudgetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await MonthlyBudgetService(db).get_or_create_budget(current_user.id, data)


@router.get("/by-month", response_model=MonthlyBudgetResponse)
async def get_budget_for_month(
    family_group_id: uuid.UUID,
    year: int,
    month: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = MonthlyBudgetService(db)
    budget = await svc.get_budget_for_month(family_group_id, year, month)
    if budget is None:
        # Create it
        data = MonthlyBudgetCreate(family_group_id=family_group_id, year=year, month=month)
        return await svc.get_or_create_budget(current_user.id, data)
    return budget


@router.get("/{budget_id}", response_model=MonthlyBudgetResponse)
async def get_budget(
    budget_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await MonthlyBudgetService(db).get_budget(budget_id)


@router.get("/{budget_id}/summary", response_model=BudgetSummaryResponse)
async def get_summary(
    budget_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await MonthlyBudgetService(db).get_summary(budget_id)


@router.post("/{budget_id}/entries", response_model=BudgetEntryResponse, status_code=201)
async def add_entry(
    budget_id: uuid.UUID,
    data: BudgetEntryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await MonthlyBudgetService(db).add_entry(current_user.id, budget_id, data)


@router.put("/entries/{entry_id}", response_model=BudgetEntryResponse)
async def update_entry(
    entry_id: uuid.UUID,
    data: BudgetEntryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await MonthlyBudgetService(db).update_entry(entry_id, data)


@router.delete("/entries/{entry_id}", status_code=204)
async def remove_entry(
    entry_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await MonthlyBudgetService(db).remove_entry(entry_id)