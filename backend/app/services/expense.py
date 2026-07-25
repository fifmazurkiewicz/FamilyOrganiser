import uuid
from datetime import date
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.expense import SimpleExpense
from app.repositories.expense import SimpleExpenseRepository
from app.schemas.expense import SimpleExpenseCreate, SimpleExpenseResponse


class SimpleExpenseService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = SimpleExpenseRepository(db)

    async def list_expenses(
        self,
        family_group_id: uuid.UUID,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> List[SimpleExpenseResponse]:
        expenses = await self.repo.list_for_family(family_group_id, start_date, end_date)
        return [SimpleExpenseResponse.model_validate(e) for e in expenses]

    async def create_expense(
        self, user_id: uuid.UUID, data: SimpleExpenseCreate
    ) -> SimpleExpenseResponse:
        expense = SimpleExpense(
            family_group_id=data.family_group_id,
            user_id=user_id,
            amount=data.amount,
            description=data.description,
            expense_date=data.expense_date,
        )
        await self.repo.add(expense)
        await self.repo.commit()
        return SimpleExpenseResponse.model_validate(expense)

    async def delete_expense(self, user_id: uuid.UUID, expense_id: uuid.UUID) -> None:
        expense = await self.repo.get_or_raise(expense_id)
        if expense.user_id != user_id:
            raise ForbiddenError("Only the owner can delete this expense")
        await self.repo.delete(expense)
        await self.repo.commit()