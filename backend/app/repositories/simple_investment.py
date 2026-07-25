import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.simple_investment import SimpleInvestment
from app.repositories.base import BaseRepository


class SimpleInvestmentRepository(BaseRepository[SimpleInvestment]):
    model = SimpleInvestment

    async def list_for_family(self, family_group_id: uuid.UUID) -> List[SimpleInvestment]:
        result = await self._session.execute(
            select(SimpleInvestment)
            .where(SimpleInvestment.family_group_id == family_group_id)
            .order_by(SimpleInvestment.created_at.desc())
        )
        return list(result.scalars().all())