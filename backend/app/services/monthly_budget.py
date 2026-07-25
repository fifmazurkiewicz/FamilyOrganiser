import uuid
from decimal import Decimal
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ForbiddenError, ConflictError
from app.models.monthly_budget import MonthlyBudget, BudgetEntry
from app.repositories.monthly_budget import MonthlyBudgetRepository, BudgetEntryRepository
from app.schemas.monthly_budget import (
    MonthlyBudgetCreate, MonthlyBudgetResponse,
    BudgetEntryCreate, BudgetEntryResponse,
    BudgetSummaryResponse,
)


class MonthlyBudgetService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.budget_repo = MonthlyBudgetRepository(db)
        self.entry_repo = BudgetEntryRepository(db)

    async def get_or_create_budget(
        self, user_id: uuid.UUID, data: MonthlyBudgetCreate
    ) -> MonthlyBudgetResponse:
        existing = await self.budget_repo.get_for_month(
            data.family_group_id, data.year, data.month
        )
        if existing:
            return MonthlyBudgetResponse.model_validate(existing)

        # Auto-copy recurring entries from the previous month
        prev_year, prev_month = (data.year, data.month - 1) if data.month > 1 else (data.year - 1, 12)
        prev_budget = await self.budget_repo.get_for_month(data.family_group_id, prev_year, prev_month)

        budget = MonthlyBudget(
            family_group_id=data.family_group_id,
            year=data.year,
            month=data.month,
        )
        await self.budget_repo.add(budget)

        if prev_budget:
            recurring_entries = [e for e in prev_budget.entries if e.is_recurring]
            for entry in recurring_entries:
                new_entry = BudgetEntry(
                    budget_id=budget.id,
                    entry_type=entry.entry_type,
                    name=entry.name,
                    amount=entry.amount,
                    is_recurring=True,
                    created_by=user_id,
                )
                self.db.add(new_entry)

        await self.budget_repo.commit()
        return MonthlyBudgetResponse.model_validate(budget)

    async def get_budget(self, budget_id: uuid.UUID) -> MonthlyBudgetResponse:
        budget = await self.budget_repo.get_or_raise(budget_id)
        return MonthlyBudgetResponse.model_validate(budget)

    async def get_budget_for_month(
        self, family_group_id: uuid.UUID, year: int, month: int
    ) -> MonthlyBudgetResponse | None:
        budget = await self.budget_repo.get_for_month(family_group_id, year, month)
        if budget is None:
            return None
        return MonthlyBudgetResponse.model_validate(budget)

    async def add_entry(
        self, user_id: uuid.UUID, budget_id: uuid.UUID, data: BudgetEntryCreate
    ) -> BudgetEntryResponse:
        entry = BudgetEntry(
            budget_id=budget_id,
            entry_type=data.entry_type,
            name=data.name,
            amount=data.amount,
            is_recurring=data.is_recurring,
            created_by=user_id,
        )
        await self.entry_repo.add(entry)
        await self.entry_repo.commit()
        return BudgetEntryResponse.model_validate(entry)

    async def remove_entry(self, entry_id: uuid.UUID) -> None:
        entry = await self.entry_repo.get_or_raise(entry_id)
        await self.entry_repo.delete(entry)
        await self.entry_repo.commit()

    async def update_entry(
        self, entry_id: uuid.UUID, data: BudgetEntryCreate
    ) -> BudgetEntryResponse:
        entry = await self.entry_repo.get_or_raise(entry_id)
        for field, value in data.model_dump().items():
            setattr(entry, field, value)
        await self.entry_repo.commit()
        return BudgetEntryResponse.model_validate(entry)

    async def get_summary(self, budget_id: uuid.UUID) -> BudgetSummaryResponse:
        entries = await self.entry_repo.list_for_budget(budget_id)
        total_income = Decimal("0")
        total_expenses = Decimal("0")
        for e in entries:
            if e.entry_type.value == "income":
                total_income += e.amount
            else:
                total_expenses += e.amount
        return BudgetSummaryResponse(
            total_income=total_income,
            total_expenses=total_expenses,
            remaining=total_income - total_expenses,
        )