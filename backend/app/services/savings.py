import uuid
from decimal import Decimal
from datetime import date
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.savings import SavingsGoal, SavingsContribution
from app.repositories.savings import SavingsGoalRepository, SavingsContributionRepository
from app.schemas.savings import (
    SavingsGoalCreate, SavingsGoalUpdate, SavingsGoalResponse,
    ContributionCreate, ContributionResponse,
)


class SavingsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.goal_repo = SavingsGoalRepository(db)
        self.contrib_repo = SavingsContributionRepository(db)

    async def list_goals(self, user_id: uuid.UUID) -> List[SavingsGoalResponse]:
        goals = await self.goal_repo.list_for_user(user_id)
        return [self._to_response(g) for g in goals]

    async def create_goal(self, user_id: uuid.UUID, data: SavingsGoalCreate) -> SavingsGoalResponse:
        goal = SavingsGoal(
            user_id=user_id,
            name=data.name,
            description=data.description,
            icon=data.icon,
            color=data.color,
            target_amount=data.target_amount,
            currency=data.currency,
            goal_type=data.goal_type,
            visibility=data.visibility,
            target_date=data.target_date,
            monthly_contribution=data.monthly_contribution,
            linked_account_id=data.linked_account_id,
            family_group_id=data.family_group_id,
            priority=data.priority,
        )
        await self.goal_repo.add(goal)
        await self.goal_repo.commit()
        return self._to_response(goal)

    async def get_goal(self, user_id: uuid.UUID, goal_id: uuid.UUID) -> SavingsGoalResponse:
        goal = await self.goal_repo.get_or_raise(goal_id)
        if goal.user_id != user_id:
            raise ForbiddenError("Access denied")
        return self._to_response(goal)

    async def update_goal(self, user_id: uuid.UUID, goal_id: uuid.UUID, data: SavingsGoalUpdate) -> SavingsGoalResponse:
        goal = await self.goal_repo.get_or_raise(goal_id)
        if goal.user_id != user_id:
            raise ForbiddenError("Access denied")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(goal, field, value)
        await self.goal_repo.commit()
        return self._to_response(goal)

    async def delete_goal(self, user_id: uuid.UUID, goal_id: uuid.UUID) -> None:
        goal = await self.goal_repo.get_or_raise(goal_id)
        if goal.user_id != user_id:
            raise ForbiddenError("Access denied")
        await self.goal_repo.delete(goal)
        await self.goal_repo.commit()

    async def add_contribution(
        self, user_id: uuid.UUID, goal_id: uuid.UUID, data: ContributionCreate
    ) -> ContributionResponse:
        goal = await self.goal_repo.get_or_raise(goal_id)
        if goal.user_id != user_id:
            raise ForbiddenError("Access denied")

        contrib = SavingsContribution(
            goal_id=goal_id,
            user_id=user_id,
            amount=data.amount,
            currency=goal.currency,
            contribution_date=data.contribution_date,
            note=data.note,
            is_withdrawal=data.is_withdrawal,
            source_account_id=data.source_account_id,
        )
        self.db.add(contrib)

        if data.is_withdrawal:
            goal.current_amount = max(Decimal("0"), goal.current_amount - data.amount)
        else:
            goal.current_amount += data.amount

        if goal.current_amount >= goal.target_amount:
            goal.is_completed = True

        await self.goal_repo.commit()
        return ContributionResponse.model_validate(contrib)

    async def list_contributions(self, user_id: uuid.UUID, goal_id: uuid.UUID) -> List[ContributionResponse]:
        goal = await self.goal_repo.get_or_raise(goal_id)
        if goal.user_id != user_id:
            raise ForbiddenError("Access denied")
        contribs = await self.contrib_repo.list_for_goal(goal_id)
        return [ContributionResponse.model_validate(c) for c in contribs]

    def _to_response(self, goal: SavingsGoal) -> SavingsGoalResponse:
        resp = SavingsGoalResponse.model_validate(goal)
        if goal.target_amount > 0:
            resp.progress_percent = min(100.0, float(goal.current_amount / goal.target_amount * 100))
        return resp
