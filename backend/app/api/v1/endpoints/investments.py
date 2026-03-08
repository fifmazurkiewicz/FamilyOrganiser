import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.services.investment import InvestmentService
from app.schemas.investment import (
    InvestmentCreate, InvestmentUpdate, InvestmentResponse,
    PolishBondCreate, PolishBondResponse,
)

router = APIRouter(prefix="/investments", tags=["Investments"])


@router.get("/", response_model=list[InvestmentResponse])
async def list_investments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await InvestmentService(db).list(current_user.id)


@router.post("/", response_model=InvestmentResponse, status_code=201)
async def create_investment(
    data: InvestmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await InvestmentService(db).create(current_user.id, data)


@router.get("/{investment_id}", response_model=InvestmentResponse)
async def get_investment(
    investment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await InvestmentService(db).get(current_user.id, investment_id)


@router.patch("/{investment_id}", response_model=InvestmentResponse)
async def update_investment(
    investment_id: uuid.UUID,
    data: InvestmentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await InvestmentService(db).update(current_user.id, investment_id, data)


@router.delete("/{investment_id}", status_code=204)
async def delete_investment(
    investment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await InvestmentService(db).delete(current_user.id, investment_id)


# --- Polish Bonds ---

@router.get("/bonds/", response_model=list[PolishBondResponse])
async def list_bonds(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await InvestmentService(db).list_bonds(current_user.id)


@router.post("/bonds/", response_model=PolishBondResponse, status_code=201)
async def create_bond(
    data: PolishBondCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await InvestmentService(db).create_bond(current_user.id, data)


@router.delete("/bonds/{bond_id}", status_code=204)
async def delete_bond(
    bond_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await InvestmentService(db).delete_bond(current_user.id, bond_id)
