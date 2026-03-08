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


async def send_recurring_reminders():
    """Check recurring transactions and send reminders."""
    from datetime import timedelta
    from app.models.transaction import RecurringTransaction
    from app.models.notification import Notification, NotificationType

    today = date.today()
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(RecurringTransaction).where(RecurringTransaction.is_active == True)
        )
        recurring = result.scalars().all()

        for rec in recurring:
            # Compute next due date (monthly)
            try:
                next_due = today.replace(day=rec.day_of_month)
            except ValueError:
                continue

            if next_due < today:
                if today.month == 12:
                    next_due = next_due.replace(year=today.year + 1, month=1)
                else:
                    next_due = next_due.replace(month=today.month + 1)

            days_until = (next_due - today).days
            if days_until == rec.reminder_days_before:
                notification = Notification(
                    user_id=rec.user_id,
                    notification_type=NotificationType.RECURRING_REMINDER,
                    title=f"Przypomnienie: {rec.name}",
                    body=f"Płatność '{rec.name}' ({rec.amount} {rec.currency}) za {days_until} dni.",
                    data={"recurring_id": str(rec.id), "due_date": str(next_due)},
                )
                db.add(notification)

        await db.commit()
