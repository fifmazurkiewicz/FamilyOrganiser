import uuid
from datetime import date
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import SimpleExpense
from app.repositories.base import BaseRepository


class SimpleExpenseRepository(BaseRepository[SimpleExpense]):
    model = SimpleExpense

    async def list_for_family(
        self,
        family_group_id: uuid.UUID,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 200,
    ) -> List[SimpleExpense]:
        stmt = select(SimpleExpense).where(SimpleExpense.family_group_id == family_group_id)
        if start_date:
            stmt = stmt.where(SimpleExpense.expense_date >= start_date)
        if end_date:
            stmt = stmt.where(SimpleExpense.expense_date <= end_date)
        stmt = stmt.order_by(SimpleExpense.expense_date.desc(), SimpleExpense.created_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())