"""Monthly budget management service."""
import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.exceptions import NotFoundError
from app.models.monthly_budget import MonthlyBudget, BudgetEntry


class MonthlyBudgetService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_for_month(
        self, family_group_id: uuid.UUID, year: int, month: int
    ) -> Optional[MonthlyBudget]:
        result = await self._session.execute(
            select(MonthlyBudget).options(selectinload(MonthlyBudget.entries)).where(
                MonthlyBudget.family_group_id == family_group_id,
                MonthlyBudget.year == year,
                MonthlyBudget.month == month,
            )
        )
        return result.scalars().first()

    async def list_for_family(self, family_group_id: uuid.UUID) -> List[MonthlyBudget]:
        result = await self._session.execute(
            select(MonthlyBudget)
            .options(selectinload(MonthlyBudget.entries))
            .where(MonthlyBudget.family_group_id == family_group_id)
            .order_by(MonthlyBudget.year.desc(), MonthlyBudget.month.desc())
        )
        return list(result.scalars().unique().all())

    async def get(self, budget_id: uuid.UUID) -> MonthlyBudget:
        result = await self._session.execute(
            select(MonthlyBudget).options(selectinload(MonthlyBudget.entries)).where(MonthlyBudget.id == budget_id)
        )
        b = result.scalars().first()
        if b is None:
            raise NotFoundError(f"MonthlyBudget {budget_id} not found")
        return b

    async def create(self, data: dict) -> MonthlyBudget:
        budget = MonthlyBudget(
            family_group_id=data["family_group_id"],
            year=data["year"],
            month=data["month"],
        )
        self._session.add(budget)
        await self._session.commit()
        await self._session.refresh(budget)
        return budget

    async def delete(self, budget: MonthlyBudget) -> None:
        await self._session.delete(budget)
        await self._session.commit()

    async def list_entries(self, budget_id: uuid.UUID) -> List[BudgetEntry]:
        result = await self._session.execute(
            select(BudgetEntry).where(BudgetEntry.budget_id == budget_id)
        )
        return list(result.scalars().all())

    async def create_entry(self, data: dict) -> BudgetEntry:
        entry = BudgetEntry(
            budget_id=data["budget_id"],
            entry_type=data["entry_type"],
            name=data["name"],
            amount=data["amount"],
            is_recurring=data.get("is_recurring", False),
            created_by=data["created_by"],
        )
        self._session.add(entry)
        await self._session.commit()
        await self._session.refresh(entry)
        return entry

    async def update_entry(self, entry: BudgetEntry, data: dict) -> BudgetEntry:
        for key, value in data.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        await self._session.commit()
        await self._session.refresh(entry)
        return entry

    async def delete_entry(self, entry: BudgetEntry) -> None:
        await self._session.delete(entry)
        await self._session.commit()
