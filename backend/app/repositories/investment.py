import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.investment import Investment, PolishBond
from app.repositories.base import BaseRepository


class InvestmentRepository(BaseRepository[Investment]):
    model = Investment

    async def list_for_user(self, user_id: uuid.UUID) -> List[Investment]:
        result = await self._session.execute(
            select(Investment)
            .where(Investment.user_id == user_id)
            .order_by(Investment.created_at.desc())
        )
        return list(result.scalars().all())


class PolishBondRepository(BaseRepository[PolishBond]):
    model = PolishBond

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_for_user(self, user_id: uuid.UUID) -> List[PolishBond]:
        result = await self._session.execute(
            select(PolishBond)
            .where(PolishBond.user_id == user_id, PolishBond.is_active == True)
            .order_by(PolishBond.purchase_date.desc())
        )
        return list(result.scalars().all())
