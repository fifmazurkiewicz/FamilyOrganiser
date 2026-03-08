import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import Budget, BudgetCategory
from app.repositories.base import BaseRepository


class BudgetRepository(BaseRepository[Budget]):
    model = Budget

    async def list_for_user(self, user_id: uuid.UUID) -> list[Budget]:
        result = await self.session.execute(
            select(Budget).where(Budget.user_id == user_id).order_by(Budget.year.desc(), Budget.month.desc())
        )
        return list(result.scalars().all())

    async def get_with_categories(self, budget_id: uuid.UUID) -> Budget | None:
        result = await self.session.execute(select(Budget).where(Budget.id == budget_id))
        return result.scalar_one_or_none()


class BudgetCategoryRepository(BaseRepository[BudgetCategory]):
    model = BudgetCategory

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_for_budget(self, budget_id: uuid.UUID) -> list[BudgetCategory]:
        result = await self.session.execute(
            select(BudgetCategory).where(BudgetCategory.budget_id == budget_id)
        )
        return list(result.scalars().all())
