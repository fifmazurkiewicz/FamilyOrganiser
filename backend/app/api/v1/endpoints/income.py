import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.services.income import IncomeService
from app.schemas.income import (
    IncomeCreate, IncomeUpdate, IncomeResponse,
    IncomeTemplateCreate, IncomeTemplateResponse,
)

router = APIRouter(prefix="/income", tags=["Income"])


# --- Templates ---

@router.get("/templates", response_model=list[IncomeTemplateResponse])
async def list_templates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await IncomeService(db).list_templates(current_user.id)


@router.post("/templates", response_model=IncomeTemplateResponse, status_code=201)
async def create_template(
    data: IncomeTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await IncomeService(db).create_template(current_user.id, data)


@router.delete("/templates/{template_id}", status_code=204)
async def delete_template(
    template_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await IncomeService(db).delete_template(current_user.id, template_id)


# --- Incomes ---

@router.get("/", response_model=list[IncomeResponse])
async def list_incomes(
    year: Optional[int] = None,
    month: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await IncomeService(db).list(current_user.id, year=year, month=month)


@router.post("/", response_model=IncomeResponse, status_code=201)
async def create_income(
    data: IncomeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await IncomeService(db).create(current_user.id, data)


@router.patch("/{income_id}", response_model=IncomeResponse)
async def update_income(
    income_id: uuid.UUID,
    data: IncomeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await IncomeService(db).update(current_user.id, income_id, data)


@router.delete("/{income_id}", status_code=204)
async def delete_income(
    income_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await IncomeService(db).delete(current_user.id, income_id)
