"""Savings goal management service."""
import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import NotFoundError
from app.models.savings import SavingsGoal, SavingsContribution, SavingsGoalMember


class SavingsService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_goals(self, user_id: uuid.UUID) -> List[SavingsGoal]:
        result = await self._session.execute(
            select(SavingsGoal)
            .where(SavingsGoal.user_id == user_id, SavingsGoal.is_active == True)
            .order_by(SavingsGoal.priority.desc(), SavingsGoal.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_goal(self, goal_id: uuid.UUID) -> SavingsGoal:
        goal = await self._session.get(SavingsGoal, goal_id)
        if not goal:
            raise NotFoundError("Savings goal not found")
        return goal

    async def create_goal(self, data: dict) -> SavingsGoal:
        goal = SavingsGoal(
            user_id=data["user_id"],
            family_group_id=data.get("family_group_id"),
            linked_account_id=data.get("linked_account_id"),
            name=data["name"],
            description=data.get("description"),
            icon=data.get("icon"),
            color=data.get("color"),
            target_amount=data["target_amount"],
            currency=data.get("currency", "PLN"),
            goal_type=data.get("goal_type", "personal"),
            visibility=data.get("visibility", "private"),
            target_date=data.get("target_date"),
            monthly_contribution=data.get("monthly_contribution"),
            priority=data.get("priority", 0),
        )
        self._session.add(goal)
        await self._session.commit()
        await self._session.refresh(goal)
        return goal

    async def update_goal(self, goal: SavingsGoal, data: dict) -> SavingsGoal:
        for key, value in data.items():
            if value is not None and hasattr(goal, key):
                setattr(goal, key, value)
        await self._session.commit()
        await self._session.refresh(goal)
        return goal

    async def delete_goal(self, goal: SavingsGoal) -> None:
        await self._session.delete(goal)
        await self._session.commit()

    async def list_contributions(self, goal_id: uuid.UUID) -> List[SavingsContribution]:
        result = await self._session.execute(
            select(SavingsContribution)
            .where(SavingsContribution.goal_id == goal_id)
            .order_by(SavingsContribution.contribution_date.desc())
        )
        return list(result.scalars().all())

    async def create_contribution(self, data: dict) -> SavingsContribution:
        contribution = SavingsContribution(
            goal_id=data["goal_id"],
            user_id=data["user_id"],
            source_account_id=data.get("source_account_id"),
            amount=data["amount"],
            currency=data.get("currency", "PLN"),
            contribution_date=data["contribution_date"],
            note=data.get("note"),
            is_withdrawal=data.get("is_withdrawal", False),
        )
        self._session.add(contribution)
        goal = await self._session.get(SavingsGoal, data["goal_id"])
        if goal:
            if data.get("is_withdrawal"):
                goal.current_amount = max(goal.current_amount - data["amount"], 0)
            else:
                goal.current_amount += data["amount"]
        await self._session.commit()
        await self._session.refresh(contribution)
        return contribution

    async def list_goal_members(self, goal_id: uuid.UUID) -> List[SavingsGoalMember]:
        result = await self._session.execute(
            select(SavingsGoalMember).where(SavingsGoalMember.goal_id == goal_id)
        )
        return list(result.scalars().all())

    async def add_goal_member(self, data: dict) -> SavingsGoalMember:
        member = SavingsGoalMember(
            goal_id=data["goal_id"],
            user_id=data["user_id"],
        )
        self._session.add(member)
        await self._session.commit()
        await self._session.refresh(member)
        return member
