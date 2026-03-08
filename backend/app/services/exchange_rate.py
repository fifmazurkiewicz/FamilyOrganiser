"""Exchange rate conversion service."""
from decimal import Decimal
from typing import Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exchange_rate import ExchangeRate


class ExchangeRateService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_latest(self, currency: str) -> ExchangeRate | None:
        result = await self._session.execute(
            select(ExchangeRate)
            .where(ExchangeRate.currency == currency)
            .order_by(desc(ExchangeRate.rate_date))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def convert(
        self, amount: Decimal, currency: str
    ) -> tuple[Decimal, Optional[Decimal]]:
        """Return (amount_pln, exchange_rate). If currency is PLN returns (amount, None)."""
        if currency == "PLN":
            return amount, None
        rate_obj = await self.get_latest(currency)
        if rate_obj:
            return amount * rate_obj.rate_to_pln, rate_obj.rate_to_pln
        return amount, None

    async def get_all_latest(self) -> dict[str, dict]:
        currencies = ["EUR", "USD", "GBP", "JPY"]
        rates: dict[str, dict] = {}
        for currency in currencies:
            rate = await self.get_latest(currency)
            if rate:
                rates[currency] = {
                    "rate": str(rate.rate_to_pln),
                    "date": str(rate.rate_date),
                    "source": rate.source,
                }
        return rates
