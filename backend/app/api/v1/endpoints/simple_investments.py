import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_approved
from app.db.base import get_db
from app.models.user import User
from app.services.simple_investment import SimpleInvestmentService
from app.schemas.simple_investment import (
    SimpleInvestmentCreate, SimpleInvestmentUpdate,
    SimpleInvestmentResponse, InvestmentSummaryResponse,
)

router = APIRouter(
    prefix="/simple-investments",
    tags=["Simple Investments"],
    dependencies=[Depends(require_approved)],
)


@router.get("/", response_model=list[SimpleInvestmentResponse])
async def list_investments(
    family_group_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SimpleInvestmentService(db).list_investments(current_user.id, family_group_id)


@router.post("/", response_model=SimpleInvestmentResponse, status_code=201)
async def create_investment(
    data: SimpleInvestmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SimpleInvestmentService(db).create_investment(current_user.id, data)


@router.get("/summary", response_model=InvestmentSummaryResponse)
async def get_summary(
    family_group_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SimpleInvestmentService(db).get_summary(current_user.id, family_group_id)


@router.get("/{investment_id}", response_model=SimpleInvestmentResponse)
async def get_investment(
    investment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SimpleInvestmentService(db).get_investment(current_user.id, investment_id)


@router.patch("/{investment_id}", response_model=SimpleInvestmentResponse)
async def update_investment(
    investment_id: uuid.UUID,
    data: SimpleInvestmentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SimpleInvestmentService(db).update_investment(current_user.id, investment_id, data)


@router.delete("/{investment_id}", status_code=204)
async def delete_investment(
    investment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await SimpleInvestmentService(db).delete_investment(current_user.id, investment_id)
