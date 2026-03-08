"""Reporting and analytics service."""
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.income import Income
from app.models.savings import SavingsGoal
from app.models.transaction import Transaction, TransactionCategory, TransactionType


class ReportService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def dashboard(self, user_id: UUID) -> dict:
        today = date.today()

        total_balance = await self._scalar(
            select(func.sum(Account.current_balance)).where(
                Account.owner_id == user_id, Account.is_active == True
            )
        )
        month_expenses = await self._scalar(
            select(func.sum(Transaction.amount)).where(
                Transaction.user_id == user_id,
                Transaction.transaction_type == TransactionType.EXPENSE,
                extract("year", Transaction.transaction_date) == today.year,
                extract("month", Transaction.transaction_date) == today.month,
            )
        )
        month_income = await self._scalar(
            select(func.sum(Income.amount)).where(
                Income.user_id == user_id,
                Income.is_skipped == False,
                extract("year", Income.income_date) == today.year,
                extract("month", Income.income_date) == today.month,
            )
        )
        total_savings = await self._scalar(
            select(func.sum(SavingsGoal.current_amount)).where(
                SavingsGoal.user_id == user_id, SavingsGoal.is_active == True
            )
        )

        expenses = total_balance if total_balance is not None else Decimal("0")
        income = month_income if month_income is not None else Decimal("0")
        exp = month_expenses if month_expenses is not None else Decimal("0")

        return {
            "total_balance": str(total_balance or Decimal("0")),
            "month_expenses": str(exp),
            "month_income": str(income),
            "total_savings": str(total_savings or Decimal("0")),
            "cashflow": str(income - exp),
        }

    async def expenses_by_category(
        self, user_id: UUID, year: int, month: Optional[int] = None
    ) -> list[dict]:
        conditions = [
            Transaction.user_id == user_id,
            Transaction.transaction_type == TransactionType.EXPENSE,
            extract("year", Transaction.transaction_date) == year,
        ]
        if month:
            conditions.append(extract("month", Transaction.transaction_date) == month)

        result = await self._session.execute(
            select(
                TransactionCategory.name,
                func.sum(Transaction.amount).label("total"),
            )
            .join(
                TransactionCategory,
                Transaction.category_id == TransactionCategory.id,
                isouter=True,
            )
            .where(and_(*conditions))
            .group_by(TransactionCategory.name)
            .order_by(func.sum(Transaction.amount).desc())
        )
        return [
            {"category": row[0] or "Bez kategorii", "amount": str(row[1])}
            for row in result.all()
        ]

    async def monthly_trend(self, user_id: UUID, months: int = 12) -> list[dict]:
        today = date.today()
        result = []

        for i in range(months - 1, -1, -1):
            month_num = today.month - i
            year = today.year
            while month_num <= 0:
                month_num += 12
                year -= 1

            expenses = await self._scalar(
                select(func.sum(Transaction.amount)).where(
                    Transaction.user_id == user_id,
                    Transaction.transaction_type == TransactionType.EXPENSE,
                    extract("year", Transaction.transaction_date) == year,
                    extract("month", Transaction.transaction_date) == month_num,
                )
            ) or Decimal("0")

            income = await self._scalar(
                select(func.sum(Income.amount)).where(
                    Income.user_id == user_id,
                    Income.is_skipped == False,
                    extract("year", Income.income_date) == year,
                    extract("month", Income.income_date) == month_num,
                )
            ) or Decimal("0")

            result.append(
                {
                    "year": year,
                    "month": month_num,
                    "label": f"{year}-{month_num:02d}",
                    "expenses": str(expenses),
                    "income": str(income),
                    "cashflow": str(income - expenses),
                }
            )
        return result

    async def _scalar(self, stmt) -> Optional[Decimal]:
        result = await self._session.execute(stmt)
        return result.scalar()
