import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.monthly_budget import MonthlyBudget, BudgetEntry
from app.repositories.base import BaseRepository


class MonthlyBudgetRepository(BaseRepository[MonthlyBudget]):
    model = MonthlyBudget

    async def get_for_month(
        self, family_group_id: uuid.UUID, year: int, month: int
    ) -> Optional[MonthlyBudget]:
        result = await self._session.execute(
            select(MonthlyBudget).where(
                MonthlyBudget.family_group_id == family_group_id,
                MonthlyBudget.year == year,
                MonthlyBudget.month == month,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_family(self, family_group_id: uuid.UUID) -> List[MonthlyBudget]:
        result = await self._session.execute(
            select(MonthlyBudget)
            .where(MonthlyBudget.family_group_id == family_group_id)
            .order_by(MonthlyBudget.year.desc(), MonthlyBudget.month.desc())
        )
        return list(result.scalars().all())


class BudgetEntryRepository(BaseRepository[BudgetEntry]):
    model = BudgetEntry

    async def list_for_budget(self, budget_id: uuid.UUID) -> List[BudgetEntry]:
        result = await self._session.execute(
            select(BudgetEntry).where(BudgetEntry.budget_id == budget_id)
        )
        return list(result.scalars().all())