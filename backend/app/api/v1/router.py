"""API v1 — aggregated router."""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    exchange_rates,
    family,
    monthly_budgets,
    notifications,
    reports,
    shopping,
    simple_investments,
    tasks,
    users,
)

router = APIRouter(prefix="/v1")

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(family.router)
router.include_router(reports.router)
router.include_router(notifications.router)
router.include_router(exchange_rates.router)
router.include_router(shopping.router)
router.include_router(tasks.router)
router.include_router(monthly_budgets.router)
router.include_router(simple_investments.router)
