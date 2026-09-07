from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_approved
from app.db.base import get_db
from app.models.user import User
from app.services.exchange_rate import ExchangeRateService

router = APIRouter(
    prefix="/exchange-rates",
    tags=["Exchange Rates"],
    dependencies=[Depends(require_approved)],
)


@router.get("/")
async def get_all_rates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ExchangeRateService(db).get_all_latest()


@router.get("/{currency}")
async def get_rate(
    currency: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rate = await ExchangeRateService(db).get_latest(currency.upper())
    return {"currency": currency.upper(), "rate_to_pln": float(rate) if rate else None}
