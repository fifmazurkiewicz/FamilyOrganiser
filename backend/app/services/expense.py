"""Simple expense management service."""
import uuid
from datetime import date
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.expense import SimpleExpense
from app.schemas.expense import SimpleExpenseCreate


class SimpleExpenseService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_expense(self, user_id: uuid.UUID, data: SimpleExpenseCreate) -> SimpleExpense:
        expense = SimpleExpense(
            family_group_id=data.family_group_id,
            user_id=user_id,
            amount=data.amount,
            description=data.description,
            expense_date=data.expense_date,
        )
        self._session.add(expense)
        await self._session.commit()
        await self._session.refresh(expense)
        return expense

    async def list_expenses(
        self,
        family_group_id: uuid.UUID,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 200,
    ) -> List[SimpleExpense]:
        stmt = select(SimpleExpense).where(SimpleExpense.family_group_id == family_group_id)
        if start_date:
            stmt = stmt.where(SimpleExpense.expense_date >= start_date)
        if end_date:
            stmt = stmt.where(SimpleExpense.expense_date <= end_date)
        stmt = stmt.order_by(SimpleExpense.expense_date.desc(), SimpleExpense.created_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def delete_expense(self, user_id: uuid.UUID, expense_id: uuid.UUID) -> None:
        expense = await self._session.get(SimpleExpense, expense_id)
        if not expense:
            raise NotFoundError("Expense not found")
        if expense.user_id != user_id:
            raise ForbiddenError("Not your expense")
        await self._session.delete(expense)
        await self._session.commit()
