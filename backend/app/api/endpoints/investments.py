import uuid
from datetime import date, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import get_db
from app.models.user import User
from app.models.investment import Investment, PolishBond, BondType
from app.schemas.investment import (
    InvestmentCreate, InvestmentUpdate, InvestmentResponse,
    PolishBondCreate, PolishBondResponse,
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/investments", tags=["investments"])

# Bond periods in years
BOND_PERIODS = {
    BondType.OFL: 0.25,
    BondType.ROR: 1,
    BondType.DOR: 2,
    BondType.TOS: 3,
    BondType.COI: 4,
    BondType.EDO: 10,
    BondType.ROS: 6,
    BondType.ROD: 12,
}


def _compute_maturity_date(purchase_date: date, bond_type: BondType) -> date:
    years = BOND_PERIODS.get(bond_type, 1)
    months = int(years * 12)
    result = purchase_date
    year = result.year + months // 12
    month = result.month + months % 12
    if month > 12:
        year += 1
        month -= 12
    return result.replace(year=year, month=month)


def _compute_accrued_interest(bond: PolishBond) -> Decimal:
    """Simple linear interest accrual for current period."""
    today = date.today()
    if today >= bond.maturity_date:
        return bond.quantity * Decimal("100") * bond.first_period_rate
    days_total = (bond.maturity_date - bond.purchase_date).days
    days_elapsed = (today - bond.purchase_date).days
    if days_total == 0:
        return Decimal("0")
    fraction = Decimal(str(days_elapsed)) / Decimal(str(days_total))
    return bond.quantity * Decimal("100") * bond.first_period_rate * fraction


def _bond_to_response(bond: PolishBond) -> PolishBondResponse:
    nominal = bond.quantity * Decimal("100")
    accrued = _compute_accrued_interest(bond)
    current_value = nominal + accrued
    return PolishBondResponse(
        id=bond.id,
        bond_type=bond.bond_type,
        series=bond.series,
        quantity=bond.quantity,
        purchase_date=bond.purchase_date,
        maturity_date=bond.maturity_date,
        first_period_rate=bond.first_period_rate,
        current_value=current_value,
        nominal_value=nominal,
        accrued_interest=accrued,
        is_active=bond.is_active,
        notes=bond.notes,
    )


def _investment_to_response(inv: Investment) -> InvestmentResponse:
    total_value = None
    roi_percent = None
    if inv.quantity and inv.current_price:
        total_value = inv.quantity * inv.current_price
        if inv.purchase_price and inv.purchase_price > 0:
            roi_percent = float((inv.current_price - inv.purchase_price) / inv.purchase_price * 100)
    return InvestmentResponse(
        id=inv.id,
        user_id=inv.user_id,
        investment_type=inv.investment_type,
        name=inv.name,
        ticker=inv.ticker,
        quantity=inv.quantity,
        purchase_price=inv.purchase_price,
        current_price=inv.current_price,
        currency=inv.currency,
        purchase_date=inv.purchase_date,
        is_shared=inv.is_shared,
        total_value=total_value,
        roi_percent=roi_percent,
        created_at=inv.created_at,
    )


@router.post("/", response_model=InvestmentResponse, status_code=201)
async def create_investment(
    payload: InvestmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    inv = Investment(user_id=current_user.id, **payload.model_dump())
    db.add(inv)
    await db.commit()
    await db.refresh(inv)
    return _investment_to_response(inv)


@router.get("/", response_model=list[InvestmentResponse])
async def list_investments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Investment).where(Investment.user_id == current_user.id)
    )
    return [_investment_to_response(i) for i in result.scalars().all()]


@router.patch("/{investment_id}", response_model=InvestmentResponse)
async def update_investment(
    investment_id: uuid.UUID,
    payload: InvestmentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Investment).where(
            Investment.id == investment_id, Investment.user_id == current_user.id
        )
    )
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Investment not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(inv, field, value)
    await db.commit()
    await db.refresh(inv)
    return _investment_to_response(inv)


@router.delete("/{investment_id}")
async def delete_investment(
    investment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Investment).where(
            Investment.id == investment_id, Investment.user_id == current_user.id
        )
    )
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Investment not found")
    await db.delete(inv)
    await db.commit()
    return {"message": "Investment deleted"}


# Polish bonds
@router.post("/bonds", response_model=PolishBondResponse, status_code=201)
async def create_bond(
    payload: PolishBondCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    maturity = _compute_maturity_date(payload.purchase_date, payload.bond_type)
    bond = PolishBond(
        user_id=current_user.id,
        bond_type=payload.bond_type,
        series=payload.series,
        quantity=payload.quantity,
        purchase_date=payload.purchase_date,
        maturity_date=maturity,
        first_period_rate=payload.first_period_rate,
        notes=payload.notes,
    )
    db.add(bond)
    await db.commit()
    await db.refresh(bond)
    return _bond_to_response(bond)


@router.get("/bonds", response_model=list[PolishBondResponse])
async def list_bonds(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PolishBond).where(
            PolishBond.user_id == current_user.id, PolishBond.is_active == True
        )
    )
    return [_bond_to_response(b) for b in result.scalars().all()]
