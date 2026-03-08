from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.db.base import engine, Base
from app.services.seed import seed_categories
from app.db.base import AsyncSessionLocal
from app.api.endpoints import (
    auth, users, family, accounts, transactions,
    budgets, savings, investments, income,
    notifications, reports, exchange_rates, transfers,
)

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed default data
    async with AsyncSessionLocal() as db:
        await seed_categories(db)

    # Schedule tasks
    from app.tasks.exchange_rate_fetcher import fetch_and_store_exchange_rates, send_recurring_reminders

    scheduler.add_job(
        fetch_and_store_exchange_rates,
        CronTrigger(hour=settings.EXCHANGE_RATE_FETCH_HOUR, minute=0),
        id="fetch_exchange_rates",
        replace_existing=True,
    )
    scheduler.add_job(
        send_recurring_reminders,
        CronTrigger(hour=7, minute=0),
        id="send_recurring_reminders",
        replace_existing=True,
    )
    scheduler.start()

    yield

    scheduler.shutdown()


app = FastAPI(
    title="FamilyOrganiser API",
    version="1.0.0",
    description="Prywatna aplikacja do zarządzania finansami rodzinnymi",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(family.router, prefix="/api")
app.include_router(accounts.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")
app.include_router(budgets.router, prefix="/api")
app.include_router(savings.router, prefix="/api")
app.include_router(investments.router, prefix="/api")
app.include_router(income.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(exchange_rates.router, prefix="/api")
app.include_router(transfers.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "FamilyOrganiser API"}
