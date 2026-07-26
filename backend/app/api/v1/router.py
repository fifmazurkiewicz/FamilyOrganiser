"""API v1 — aggregated router."""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    accounts,
    auth,
    budgets,
    exchange_rates,
    family,
    income,
    investments,
    monthly_budgets,
    notifications,
    reports,
    savings,
    shopping,
    simple_expenses,
    simple_investments,
    tasks,
    transactions,
    transfers,
    users,
)

router = APIRouter(prefix="/v1")

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(family.router)
router.include_router(accounts.router)
router.include_router(transactions.router)
router.include_router(budgets.router)
router.include_router(savings.router)
router.include_router(investments.router)
router.include_router(income.router)
router.include_router(transfers.router)
router.include_router(reports.router)
router.include_router(notifications.router)
router.include_router(exchange_rates.router)
router.include_router(shopping.router)
router.include_router(tasks.router)
router.include_router(simple_expenses.router)
router.include_router(monthly_budgets.router)
router.include_router(simple_investments.router)
