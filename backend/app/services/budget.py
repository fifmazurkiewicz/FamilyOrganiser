import uuid
from decimal import Decimal
from datetime import date

from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.budget import Budget, BudgetCategory
from app.models.transaction import Transaction, TransactionCategory
from app.repositories.budget import BudgetRepository, BudgetCategoryRepository
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse, BudgetCategoryResponse


class BudgetService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = BudgetRepository(db)
        self.cat_repo = BudgetCategoryRepository(db)

    async def list(self, user_id: uuid.UUID) -> list[BudgetResponse]:
        budgets = await self.repo.list_for_user(user_id)
        result = []
        for b in budgets:
            cats = await self._enrich_categories(b, user_id)
            resp = BudgetResponse.model_validate(b)
            resp.categories = cats
            result.append(resp)
        return result

    async def create(self, user_id: uuid.UUID, data: BudgetCreate) -> BudgetResponse:
        budget = Budget(
            user_id=user_id,
            name=data.name,
            scope=data.scope,
            year=data.year,
            month=data.month,
            family_group_id=data.family_group_id,
            alert_threshold_percent=data.alert_threshold_percent,
        )
        await self.repo.add(budget)
        await self.db.flush()

        for cat_data in data.categories:
            bc = BudgetCategory(
                budget_id=budget.id,
                category_id=cat_data.category_id,
                planned_amount=cat_data.planned_amount,
                currency=cat_data.currency,
            )
            self.db.add(bc)

        await self.repo.commit()
        await self.db.refresh(budget)
        cats = await self._enrich_categories(budget, user_id)
        resp = BudgetResponse.model_validate(budget)
        resp.categories = cats
        return resp

    async def get(self, user_id: uuid.UUID, budget_id: uuid.UUID) -> BudgetResponse:
        budget = await self.repo.get_or_raise(budget_id)
        if budget.user_id != user_id:
            raise ForbiddenError("Access denied")
        cats = await self._enrich_categories(budget, user_id)
        resp = BudgetResponse.model_validate(budget)
        resp.categories = cats
        return resp

    async def update(self, user_id: uuid.UUID, budget_id: uuid.UUID, data: BudgetUpdate) -> BudgetResponse:
        budget = await self.repo.get_or_raise(budget_id)
        if budget.user_id != user_id:
            raise ForbiddenError("Access denied")
        if data.name is not None:
            budget.name = data.name
        if data.alert_threshold_percent is not None:
            budget.alert_threshold_percent = data.alert_threshold_percent
        await self.repo.commit()
        cats = await self._enrich_categories(budget, user_id)
        resp = BudgetResponse.model_validate(budget)
        resp.categories = cats
        return resp

    async def delete(self, user_id: uuid.UUID, budget_id: uuid.UUID) -> None:
        budget = await self.repo.get_or_raise(budget_id)
        if budget.user_id != user_id:
            raise ForbiddenError("Access denied")
        await self.repo.delete(budget)
        await self.repo.commit()

    async def _enrich_categories(self, budget: Budget, user_id: uuid.UUID) -> list[BudgetCategoryResponse]:
        cats = await self.cat_repo.list_for_budget(budget.id)
        result = []
        for bc in cats:
            actual = await self._get_actual_spending(user_id, bc.category_id, budget.year, budget.month)
            resp = BudgetCategoryResponse.model_validate(bc)
            resp.actual_amount = actual
            result.append(resp)
        return result

    async def _get_actual_spending(
        self,
        user_id: uuid.UUID,
        category_id: uuid.UUID,
        year: int,
        month: int | None,
    ) -> Decimal:
        stmt = select(func.coalesce(func.sum(Transaction.amount_pln), Decimal("0"))).where(
            Transaction.user_id == user_id,
            Transaction.category_id == category_id,
            extract("year", Transaction.transaction_date) == year,
        )
        if month:
            stmt = stmt.where(extract("month", Transaction.transaction_date) == month)
        result = await self.db.execute(stmt)
        return result.scalar_one() or Decimal("0")
