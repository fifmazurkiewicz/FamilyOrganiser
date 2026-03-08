import uuid
from typing import List

from sqlalchemy import select

from app.models.income import Income, IncomeTemplate
from app.repositories.base import BaseRepository


class IncomeTemplateRepository(BaseRepository[IncomeTemplate]):
    model = IncomeTemplate

    async def list_for_user(self, user_id: uuid.UUID) -> List[IncomeTemplate]:
        result = await self._session.execute(
            select(IncomeTemplate)
            .where(IncomeTemplate.user_id == user_id, IncomeTemplate.is_active == True)
            .order_by(IncomeTemplate.created_at)
        )
        return list(result.scalars().all())


class IncomeRepository(BaseRepository[Income]):
    model = Income

    async def list_for_user(self, user_id: uuid.UUID, year: int | None = None, month: int | None = None) -> List[Income]:
        stmt = select(Income).where(Income.user_id == user_id)
        if year:
            from sqlalchemy import extract
            stmt = stmt.where(extract("year", Income.income_date) == year)
        if month:
            from sqlalchemy import extract
            stmt = stmt.where(extract("month", Income.income_date) == month)
        stmt = stmt.order_by(Income.income_date.desc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
