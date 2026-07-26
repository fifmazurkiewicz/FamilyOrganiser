import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.services.expense import SimpleExpenseService
from app.schemas.expense import SimpleExpenseCreate, SimpleExpenseResponse

router = APIRouter(prefix="/simple-expenses", tags=["Simple Expenses"])


@router.get("/", response_model=list[SimpleExpenseResponse])
async def list_expenses(
    family_group_id: uuid.UUID = Query(...),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SimpleExpenseService(db).list_expenses(
        family_group_id, start_date, end_date
    )


@router.post("/", response_model=SimpleExpenseResponse, status_code=201)
async def create_expense(
    data: SimpleExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SimpleExpenseService(db).create_expense(current_user.id, data)


@router.delete("/{expense_id}", status_code=204)
async def delete_expense(
    expense_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await SimpleExpenseService(db).delete_expense(current_user.id, expense_id)