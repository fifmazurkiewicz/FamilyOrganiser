"""
Scheduled task: fetch daily exchange rates from NBP API.
Runs once per day at 08:00 (after NBP publishes table A).
"""
import httpx
import logging
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.db.base import AsyncSessionLocal
from app.models.exchange_rate import ExchangeRate

logger = logging.getLogger(__name__)

NBP_URL = "https://api.nbp.pl/api/exchangerates/tables/A/?format=json"
SUPPORTED_CURRENCIES = {"EUR", "USD", "GBP", "JPY"}


async def fetch_and_store_exchange_rates():
    """Fetch exchange rates from NBP API and store in DB."""
    today = date.today()
    logger.info("Fetching exchange rates from NBP for %s", today)

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(NBP_URL)
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        logger.error("Failed to fetch exchange rates from NBP: %s", e)
        return

    rates_data = data[0].get("rates", [])

    async with AsyncSessionLocal() as db:
        for rate_entry in rates_data:
            code = rate_entry.get("code", "").upper()
            if code not in SUPPORTED_CURRENCIES:
                continue

            mid_rate = Decimal(str(rate_entry.get("mid", 0)))

            # Upsert
            stmt = insert(ExchangeRate).values(
                currency=code,
                rate_date=today,
                rate_to_pln=mid_rate,
                source="NBP",
                fetched_at=datetime.now(timezone.utc),
            ).on_conflict_do_update(
                constraint="uq_exchange_rate_currency_date",
                set_={"rate_to_pln": mid_rate, "fetched_at": datetime.now(timezone.utc)},
            )
            await db.execute(stmt)

        await db.commit()
        logger.info("Exchange rates updated successfully for %s", today)