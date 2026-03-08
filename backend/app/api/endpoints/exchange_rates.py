from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.base import get_db
from app.models.user import User
from app.models.exchange_rate import ExchangeRate
from app.api.deps import get_current_user

router = APIRouter(prefix="/exchange-rates", tags=["exchange_rates"])


@router.get("/latest")
async def get_latest_rates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get latest exchange rates for major currencies."""
    currencies = ["EUR", "USD", "GBP", "JPY"]
    rates = {}
    for currency in currencies:
        result = await db.execute(
            select(ExchangeRate).where(ExchangeRate.currency == currency)
            .order_by(desc(ExchangeRate.rate_date))
            .limit(1)
        )
        rate = result.scalar_one_or_none()
        if rate:
            rates[currency] = {
                "rate": str(rate.rate_to_pln),
                "date": str(rate.rate_date),
                "source": rate.source,
            }
    return rates
