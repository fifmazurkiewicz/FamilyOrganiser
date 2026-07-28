"""Monthly budget management service."""
import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.models.monthly_budget import BudgetEntry, BudgetEntryType, MonthlyBudget
from app.schemas.monthly_budget import (
    BudgetEntryCreate,
    BudgetEntryUpdate,
    BudgetSummaryResponse,
    MonthlyBudgetCreate,
)


class MonthlyBudgetService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_budget_for_month(
        self, family_group_id: uuid.UUID, year: int, month: int
    ) -> Optional[MonthlyBudget]:
        result = await self._session.execute(
            select(MonthlyBudget)
            .options(selectinload(MonthlyBudget.entries))
            .where(
                MonthlyBudget.family_group_id == family_group_id,
                MonthlyBudget.year == year,
                MonthlyBudget.month == month,
            )
        )
        return result.scalars().first()

    async def get_budget(self, budget_id: uuid.UUID) -> MonthlyBudget:
        result = await self._session.execute(
            select(MonthlyBudget)
            .options(selectinload(MonthlyBudget.entries))
            .where(MonthlyBudget.id == budget_id)
        )
        budget = result.scalars().first()
        if budget is None:
            raise NotFoundError(f"MonthlyBudget {budget_id} not found")
        return budget

    async def get_or_create_budget(
        self, user_id: uuid.UUID, data: MonthlyBudgetCreate
    ) -> MonthlyBudget:
        existing = await self.get_budget_for_month(
            data.family_group_id, data.year, data.month
        )
        if existing is not None:
            return existing

        budget = MonthlyBudget(
            family_group_id=data.family_group_id,
            year=data.year,
            month=data.month,
        )
        self._session.add(budget)
        await self._session.flush()

        prev_year, prev_month = self._previous_month(data.year, data.month)
        previous = await self.get_budget_for_month(
            data.family_group_id, prev_year, prev_month
        )
        if previous is not None:
            for entry in previous.entries:
                if not entry.is_recurring:
                    continue
                self._session.add(
                    BudgetEntry(
                        budget_id=budget.id,
                        entry_type=entry.entry_type,
                        name=entry.name,
                        amount=entry.amount,
                        is_recurring=True,
                        created_by=user_id,
                    )
                )

        await self._session.commit()
        return await self.get_budget(budget.id)

    async def get_summary(self, budget_id: uuid.UUID) -> BudgetSummaryResponse:
        budget = await self.get_budget(budget_id)
        total_income = Decimal("0")
        total_expenses = Decimal("0")
        for entry in budget.entries:
            if entry.entry_type == BudgetEntryType.INCOME:
                total_income += entry.amount
            else:
                total_expenses += entry.amount
        return BudgetSummaryResponse(
            total_income=total_income,
            total_expenses=total_expenses,
            remaining=total_income - total_expenses,
        )

    async def add_entry(
        self, user_id: uuid.UUID, budget_id: uuid.UUID, data: BudgetEntryCreate
    ) -> BudgetEntry:
        await self.get_budget(budget_id)
        entry = BudgetEntry(
            budget_id=budget_id,
            entry_type=data.entry_type,
            name=data.name,
            amount=data.amount,
            is_recurring=data.is_recurring,
            created_by=user_id,
        )
        self._session.add(entry)
        await self._session.commit()
        await self._session.refresh(entry)
        return entry

    async def update_entry_partial(
        self, entry_id: uuid.UUID, data: BudgetEntryUpdate | BudgetEntryCreate
    ) -> BudgetEntry:
        entry = await self._session.get(BudgetEntry, entry_id)
        if not entry:
            raise NotFoundError(f"BudgetEntry {entry_id} not found")
        for key, value in data.model_dump(exclude_none=True).items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        await self._session.commit()
        await self._session.refresh(entry)
        return entry

    async def update_entry(
        self, entry_id: uuid.UUID, data: BudgetEntryUpdate | BudgetEntryCreate
    ) -> BudgetEntry:
        return await self.update_entry_partial(entry_id, data)

    async def remove_entry(self, entry_id: uuid.UUID) -> None:
        entry = await self._session.get(BudgetEntry, entry_id)
        if not entry:
            raise NotFoundError(f"BudgetEntry {entry_id} not found")
        await self._session.delete(entry)
        await self._session.commit()

    @staticmethod
    def _previous_month(year: int, month: int) -> tuple[int, int]:
        if month == 1:
            return year - 1, 12
        return year, month - 1
