"""Income management service."""
import uuid
from typing import List
from sqlalchemy import extract, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import NotFoundError
from app.models.income import Income, IncomeTemplate


class IncomeService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_templates(self, user_id: uuid.UUID) -> List[IncomeTemplate]:
        result = await self._session.execute(
            select(IncomeTemplate)
            .where(IncomeTemplate.user_id == user_id, IncomeTemplate.is_active == True)
            .order_by(IncomeTemplate.created_at)
        )
        return list(result.scalars().all())

    async def create_template(self, data: dict, user_id: uuid.UUID) -> IncomeTemplate:
        template = IncomeTemplate(
            user_id=user_id,
            account_id=data["account_id"],
            name=data["name"],
            base_amount=data["base_amount"],
            currency=data.get("currency", "PLN"),
            category=data.get("category", "salary"),
            day_of_month=data["day_of_month"],
        )
        self._session.add(template)
        await self._session.commit()
        await self._session.refresh(template)
        return template

    async def get_template(self, template_id: uuid.UUID) -> IncomeTemplate:
        template = await self._session.get(IncomeTemplate, template_id)
        if not template:
            raise NotFoundError("Income template not found")
        return template

    async def update_template(self, template: IncomeTemplate, data: dict) -> IncomeTemplate:
        for key, value in data.items():
            if value is not None and hasattr(template, key):
                setattr(template, key, value)
        await self._session.commit()
        await self._session.refresh(template)
        return template

    async def delete_template(self, template: IncomeTemplate) -> None:
        await self._session.delete(template)
        await self._session.commit()

    async def list_incomes(
        self, user_id: uuid.UUID, year: int | None = None, month: int | None = None
    ) -> List[Income]:
        stmt = select(Income).where(Income.user_id == user_id)
        if year:
            stmt = stmt.where(extract("year", Income.income_date) == year)
        if month:
            stmt = stmt.where(extract("month", Income.income_date) == month)
        stmt = stmt.order_by(Income.income_date.desc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create_income(self, data: dict, user_id: uuid.UUID) -> Income:
        income = Income(
            user_id=user_id,
            account_id=data["account_id"],
            template_id=data.get("template_id"),
            name=data["name"],
            amount=data["amount"],
            base_amount=data.get("base_amount"),
            currency=data.get("currency", "PLN"),
            category=data.get("category", "salary"),
            income_date=data["income_date"],
            is_modified=data.get("is_modified", False),
            is_skipped=data.get("is_skipped", False),
            description=data.get("description"),
        )
        self._session.add(income)
        await self._session.commit()
        await self._session.refresh(income)
        return income

    async def get_income(self, income_id: uuid.UUID) -> Income:
        income = await self._session.get(Income, income_id)
        if not income:
            raise NotFoundError("Income not found")
        return income

    async def update_income(self, income: Income, data: dict) -> Income:
        for key, value in data.items():
            if value is not None and hasattr(income, key):
                setattr(income, key, value)
        await self._session.commit()
        await self._session.refresh(income)
        return income

    async def delete_income(self, income: Income) -> None:
        await self._session.delete(income)
        await self._session.commit()
