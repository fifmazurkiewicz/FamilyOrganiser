"""Reporting based on monthly budgets (active product stack)."""
from datetime import date
from decimal import Decimal
from typing import Any, List, Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.family import FamilyMembership
from app.models.monthly_budget import BudgetEntry, BudgetEntryType, MonthlyBudget
from app.models.simple_investment import SimpleInvestment


class ReportService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _user_group_ids(self, user_id: UUID) -> list[UUID]:
        result = await self._session.execute(
            select(FamilyMembership.family_group_id).where(
                FamilyMembership.user_id == user_id
            )
        )
        return list(result.scalars().all())

    async def _budgets_for_month(
        self, group_ids: list[UUID], year: int, month: int
    ) -> list[MonthlyBudget]:
        if not group_ids:
            return []
        result = await self._session.execute(
            select(MonthlyBudget)
            .options(selectinload(MonthlyBudget.entries))
            .where(
                MonthlyBudget.family_group_id.in_(group_ids),
                MonthlyBudget.year == year,
                MonthlyBudget.month == month,
            )
        )
        return list(result.scalars().all())

    @staticmethod
    def _sum_entries(
        budgets: list[MonthlyBudget], entry_type: BudgetEntryType
    ) -> Decimal:
        total = Decimal("0")
        for budget in budgets:
            for entry in budget.entries:
                if entry.entry_type == entry_type:
                    total += entry.amount
        return total

    async def dashboard(self, user_id: UUID) -> dict[str, Any]:
        today = date.today()
        group_ids = await self._user_group_ids(user_id)
        budgets = await self._budgets_for_month(group_ids, today.year, today.month)

        month_income = self._sum_entries(budgets, BudgetEntryType.INCOME)
        month_expenses = self._sum_entries(budgets, BudgetEntryType.EXPENSE)
        income_val = float(month_income)
        exp_val = float(month_expenses)
        savings_rate = (income_val - exp_val) / income_val * 100.0 if income_val > 0 else 0.0

        investments_total = Decimal("0")
        if group_ids:
            inv_result = await self._session.execute(
                select(func.coalesce(func.sum(SimpleInvestment.principal_amount), 0)).where(
                    SimpleInvestment.family_group_id.in_(group_ids)
                )
            )
            investments_total = Decimal(str(inv_result.scalar() or 0))

        net_worth = float(month_income - month_expenses + investments_total)
        top_expenses = await self.expenses_by_category(user_id, today.year, today.month)

        return {
            "total_assets": float(investments_total),
            "total_liabilities": 0.0,
            "net_worth": net_worth,
            "monthly_income": income_val,
            "monthly_expenses": exp_val,
            "savings_rate": round(savings_rate, 1),
            "top_expenses": top_expenses,
            "active_goals": [],
            "recent_transactions": [],
        }

    async def expenses_by_category(
        self, user_id: UUID, year: int, month: Optional[int] = None
    ) -> List[dict]:
        group_ids = await self._user_group_ids(user_id)
        if not group_ids:
            return []

        conditions = [
            MonthlyBudget.family_group_id.in_(group_ids),
            MonthlyBudget.year == year,
            BudgetEntry.entry_type == BudgetEntryType.EXPENSE,
        ]
        if month:
            conditions.append(MonthlyBudget.month == month)

        result = await self._session.execute(
            select(
                BudgetEntry.name,
                func.sum(BudgetEntry.amount).label("total"),
            )
            .join(MonthlyBudget, BudgetEntry.budget_id == MonthlyBudget.id)
            .where(and_(*conditions))
            .group_by(BudgetEntry.name)
            .order_by(func.sum(BudgetEntry.amount).desc())
        )
        return [
            {"category": row[0] or "Bez nazwy", "amount": float(row[1] or 0)}
            for row in result.all()
        ]

    async def monthly_trend(self, user_id: UUID, months: int = 12) -> List[dict]:
        today = date.today()
        group_ids = await self._user_group_ids(user_id)
        result = []

        for i in range(months - 1, -1, -1):
            month_num = today.month - i
            year = today.year
            while month_num <= 0:
                month_num += 12
                year -= 1

            budgets = await self._budgets_for_month(group_ids, year, month_num)
            income = self._sum_entries(budgets, BudgetEntryType.INCOME)
            expenses = self._sum_entries(budgets, BudgetEntryType.EXPENSE)
            result.append(
                {
                    "month": f"{year}-{month_num:02d}",
                    "income": float(income),
                    "expenses": float(expenses),
                    "savings": float(income - expenses),
                }
            )
        return result
