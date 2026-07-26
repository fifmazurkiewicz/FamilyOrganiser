"""Budget management service."""
import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.budget import Budget, BudgetCategory


class BudgetService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_user(self, user_id: uuid.UUID) -> List[Budget]:
        result = await self._session.execute(
            select(Budget).where(Budget.user_id == user_id).order_by(Budget.year.desc(), Budget.month.desc())
        )
        return list(result.scalars().all())

    async def get(self, budget_id: uuid.UUID, user_id: uuid.UUID) -> Budget:
        result = await self._session.execute(select(Budget).where(Budget.id == budget_id))
        budget = result.scalar_one_or_none()
        if not budget:
            raise NotFoundError("Budget not found")
        if budget.user_id != user_id:
            raise ForbiddenError("Access denied")
        return budget

    async def create(self, data: dict, user_id: uuid.UUID) -> Budget:
        budget = Budget(
            user_id=user_id,
            family_group_id=data.get("family_group_id"),
            name=data["name"],
            scope=data.get("scope", "personal"),
            year=data["year"],
            month=data.get("month"),
            alert_threshold_percent=data.get("alert_threshold_percent", 80),
        )
        self._session.add(budget)
        await self._session.commit()
        await self._session.refresh(budget)
        return budget

    async def update(self, budget: Budget, data: dict) -> Budget:
        for key, value in data.items():
            if value is not None and hasattr(budget, key):
                setattr(budget, key, value)
        await self._session.commit()
        await self._session.refresh(budget)
        return budget

    async def delete(self, budget: Budget) -> None:
        await self._session.delete(budget)
        await self._session.commit()

    # Categories
    async def list_categories(self, budget_id: uuid.UUID) -> List[BudgetCategory]:
        result = await self._session.execute(
            select(BudgetCategory).where(BudgetCategory.budget_id == budget_id)
        )
        return list(result.scalars().all())

    async def create_category(self, data: dict) -> BudgetCategory:
        category = BudgetCategory(
            budget_id=data["budget_id"],
            category_id=data["category_id"],
            planned_amount=data["planned_amount"],
            currency=data.get("currency", "PLN"),
        )
        self._session.add(category)
        await self._session.commit()
        await self._session.refresh(category)
        return category

    async def delete_category(self, category_id: uuid.UUID) -> None:
        category = await self._session.get(BudgetCategory, category_id)
        if not category:
            raise NotFoundError("Budget category not found")
        await self._session.delete(category)
        await self._session.commit()
