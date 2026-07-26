"""Reporting and analytics service."""
from datetime import date
from decimal import Decimal
from typing import Any, List, Optional
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

    async def dashboard(self, user_id: UUID) -> dict[str, Any]:
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
        month_income_table = await self._scalar(
            select(func.sum(Income.amount)).where(
                Income.user_id == user_id,
                Income.is_skipped == False,
                extract("year", Income.income_date) == today.year,
                extract("month", Income.income_date) == today.month,
            )
        ) or Decimal("0")
        month_income_transactions = await self._scalar(
            select(func.sum(Transaction.amount)).where(
                Transaction.user_id == user_id,
                Transaction.transaction_type == TransactionType.INCOME,
                extract("year", Transaction.transaction_date) == today.year,
                extract("month", Transaction.transaction_date) == today.month,
            )
        ) or Decimal("0")
        month_income = month_income_table + month_income_transactions
        total_savings = await self._scalar(
            select(func.sum(SavingsGoal.current_amount)).where(
                SavingsGoal.user_id == user_id, SavingsGoal.is_active == True
            )
        )

        income_val = float(month_income or Decimal("0"))
        exp_val = float(month_expenses or Decimal("0"))
        net_worth_val = float(total_balance or Decimal("0"))
        savings_rate = (income_val - exp_val) / income_val * 100.0 if income_val > 0 else 0.0

        top_expenses = await self.expenses_by_category(user_id, today.year, today.month)
        top_expenses_list = [
            {"category": e["category"], "amount": float(e["amount"])}
            for e in top_expenses
        ]

        return {
            "total_assets": net_worth_val,
            "total_liabilities": 0.0,
            "net_worth": net_worth_val,
            "monthly_income": income_val,
            "monthly_expenses": exp_val,
            "savings_rate": round(savings_rate, 1),
            "top_expenses": top_expenses_list,
            "active_goals": [],
            "recent_transactions": [],
        }

    async def expenses_by_category(
        self, user_id: UUID, year: int, month: Optional[int] = None
    ) -> List[dict]:
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

    async def monthly_trend(self, user_id: UUID, months: int = 12) -> List[dict]:
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

            income_from_table = await self._scalar(
                select(func.sum(Income.amount)).where(
                    Income.user_id == user_id,
                    Income.is_skipped == False,
                    extract("year", Income.income_date) == year,
                    extract("month", Income.income_date) == month_num,
                )
            ) or Decimal("0")

            income_from_transactions = await self._scalar(
                select(func.sum(Transaction.amount)).where(
                    Transaction.user_id == user_id,
                    Transaction.transaction_type == TransactionType.INCOME,
                    extract("year", Transaction.transaction_date) == year,
                    extract("month", Transaction.transaction_date) == month_num,
                )
            ) or Decimal("0")

            income = income_from_table + income_from_transactions

            cashflow = income - expenses
            result.append(
                {
                    "month": f"{year}-{month_num:02d}",
                    "income": float(income),
                    "expenses": float(expenses),
                    "savings": float(cashflow),
                }
            )
        return result

    async def _scalar(self, stmt) -> Optional[Decimal]:
        result = await self._session.execute(stmt)
        return result.scalar()
