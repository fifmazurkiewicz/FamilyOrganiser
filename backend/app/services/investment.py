"""Investment management service."""
import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import NotFoundError
from app.models.investment import Investment, PolishBond


class InvestmentService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_user(self, user_id: uuid.UUID) -> List[Investment]:
        result = await self._session.execute(
            select(Investment)
            .where(Investment.user_id == user_id)
            .order_by(Investment.created_at.desc())
        )
        return list(result.scalars().all())

    async def get(self, investment_id: uuid.UUID) -> Investment:
        investment = await self._session.get(Investment, investment_id)
        if not investment:
            raise NotFoundError("Investment not found")
        return investment

    async def create(self, data: dict) -> Investment:
        investment = Investment(
            user_id=data["user_id"],
            investment_type=data["investment_type"],
            name=data["name"],
            ticker=data.get("ticker"),
            quantity=data.get("quantity"),
            purchase_price=data.get("purchase_price"),
            current_price=data.get("current_price"),
            currency=data.get("currency", "PLN"),
            purchase_date=data.get("purchase_date"),
            notes=data.get("notes"),
            is_shared=data.get("is_shared", False),
            address=data.get("address"),
            rental_income_monthly=data.get("rental_income_monthly"),
            interest_rate=data.get("interest_rate"),
            maturity_date=data.get("maturity_date"),
            bank_name=data.get("bank_name"),
        )
        self._session.add(investment)
        await self._session.commit()
        await self._session.refresh(investment)
        return investment

    async def update(self, investment: Investment, data: dict) -> Investment:
        for key, value in data.items():
            if value is not None and hasattr(investment, key):
                setattr(investment, key, value)
        await self._session.commit()
        await self._session.refresh(investment)
        return investment

    async def delete(self, investment: Investment) -> None:
        await self._session.delete(investment)
        await self._session.commit()

    async def list_bonds(self, user_id: uuid.UUID) -> List[PolishBond]:
        result = await self._session.execute(
            select(PolishBond)
            .where(PolishBond.user_id == user_id, PolishBond.is_active == True)
            .order_by(PolishBond.purchase_date.desc())
        )
        return list(result.scalars().all())

    async def create_bond(self, data: dict) -> PolishBond:
        bond = PolishBond(
            user_id=data["user_id"],
            bond_type=data["bond_type"],
            series=data["series"],
            quantity=data["quantity"],
            purchase_date=data["purchase_date"],
            maturity_date=data["maturity_date"],
            first_period_rate=data["first_period_rate"],
            notes=data.get("notes"),
        )
        self._session.add(bond)
        await self._session.commit()
        await self._session.refresh(bond)
        return bond
