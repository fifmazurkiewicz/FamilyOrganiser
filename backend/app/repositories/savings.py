import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.savings import SavingsGoal, SavingsContribution, SavingsGoalMember
from app.repositories.base import BaseRepository


class SavingsGoalRepository(BaseRepository[SavingsGoal]):
    model = SavingsGoal

    async def list_for_user(self, user_id: uuid.UUID) -> List[SavingsGoal]:
        result = await self._session.execute(
            select(SavingsGoal)
            .where(SavingsGoal.user_id == user_id, SavingsGoal.is_active == True)
            .order_by(SavingsGoal.priority.desc(), SavingsGoal.created_at.desc())
        )
        return list(result.scalars().all())


class SavingsContributionRepository(BaseRepository[SavingsContribution]):
    model = SavingsContribution

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_for_goal(self, goal_id: uuid.UUID) -> List[SavingsContribution]:
        result = await self._session.execute(
            select(SavingsContribution)
            .where(SavingsContribution.goal_id == goal_id)
            .order_by(SavingsContribution.contribution_date.desc())
        )
        return list(result.scalars().all())


class SavingsGoalMemberRepository(BaseRepository[SavingsGoalMember]):
    model = SavingsGoalMember

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
