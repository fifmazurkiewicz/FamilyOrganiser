from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.services.report import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/dashboard")
async def dashboard(
    family_group_id: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ReportService(db).dashboard(current_user.id, family_group_id)


@router.get("/expenses-by-category")
async def expenses_by_category(
    year: int = Query(default=date.today().year),
    month: Optional[int] = None,
    family_group_id: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ReportService(db).expenses_by_category(
        current_user.id, year, month, family_group_id=family_group_id
    )


@router.get("/monthly-trend")
async def monthly_trend(
    months: int = Query(default=12, ge=1, le=24),
    family_group_id: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ReportService(db).monthly_trend(
        current_user.id, months, family_group_id=family_group_id
    )
