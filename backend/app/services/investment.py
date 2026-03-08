import uuid
from decimal import Decimal
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError
from app.models.investment import Investment, PolishBond, BondType
from app.repositories.investment import InvestmentRepository, PolishBondRepository
from app.schemas.investment import (
    InvestmentCreate, InvestmentUpdate, InvestmentResponse,
    PolishBondCreate, PolishBondResponse,
)


# Bond duration in years by type
_BOND_YEARS: dict[BondType, int] = {
    BondType.OFL: 0,   # 3-month, treated as <1yr
    BondType.ROR: 1,
    BondType.DOR: 2,
    BondType.TOS: 3,
    BondType.COI: 4,
    BondType.EDO: 10,
    BondType.ROS: 6,
    BondType.ROD: 12,
}


class InvestmentService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = InvestmentRepository(db)
        self.bond_repo = PolishBondRepository(db)

    async def list(self, user_id: uuid.UUID) -> list[InvestmentResponse]:
        investments = await self.repo.list_for_user(user_id)
        return [self._to_response(inv) for inv in investments]

    async def create(self, user_id: uuid.UUID, data: InvestmentCreate) -> InvestmentResponse:
        inv = Investment(user_id=user_id, **data.model_dump())
        await self.repo.add(inv)
        await self.repo.commit()
        return self._to_response(inv)

    async def get(self, user_id: uuid.UUID, investment_id: uuid.UUID) -> InvestmentResponse:
        inv = await self.repo.get_or_raise(investment_id)
        if inv.user_id != user_id:
            raise ForbiddenError("Access denied")
        return self._to_response(inv)

    async def update(self, user_id: uuid.UUID, investment_id: uuid.UUID, data: InvestmentUpdate) -> InvestmentResponse:
        inv = await self.repo.get_or_raise(investment_id)
        if inv.user_id != user_id:
            raise ForbiddenError("Access denied")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(inv, field, value)
        await self.repo.commit()
        return self._to_response(inv)

    async def delete(self, user_id: uuid.UUID, investment_id: uuid.UUID) -> None:
        inv = await self.repo.get_or_raise(investment_id)
        if inv.user_id != user_id:
            raise ForbiddenError("Access denied")
        await self.repo.delete(inv)
        await self.repo.commit()

    # --- Polish Bonds ---

    async def list_bonds(self, user_id: uuid.UUID) -> list[PolishBondResponse]:
        bonds = await self.bond_repo.list_for_user(user_id)
        return [self._bond_to_response(b) for b in bonds]

    async def create_bond(self, user_id: uuid.UUID, data: PolishBondCreate) -> PolishBondResponse:
        years = _BOND_YEARS.get(data.bond_type, 1)
        from dateutil.relativedelta import relativedelta
        if data.bond_type == BondType.OFL:
            from datetime import timedelta
            maturity = data.purchase_date + timedelta(days=90)
        else:
            maturity = data.purchase_date + relativedelta(years=years)

        bond = PolishBond(
            user_id=user_id,
            bond_type=data.bond_type,
            series=data.series,
            quantity=data.quantity,
            purchase_date=data.purchase_date,
            maturity_date=maturity,
            first_period_rate=data.first_period_rate,
            notes=data.notes,
        )
        await self.bond_repo.add(bond)
        await self.bond_repo.commit()
        return self._bond_to_response(bond)

    async def delete_bond(self, user_id: uuid.UUID, bond_id: uuid.UUID) -> None:
        bond = await self.bond_repo.get_or_raise(bond_id)
        if bond.user_id != user_id:
            raise ForbiddenError("Access denied")
        bond.is_active = False
        await self.bond_repo.commit()

    def _to_response(self, inv: Investment) -> InvestmentResponse:
        resp = InvestmentResponse.model_validate(inv)
        if inv.quantity and inv.current_price:
            resp.total_value = inv.quantity * inv.current_price
        if inv.quantity and inv.purchase_price and inv.current_price:
            cost = inv.quantity * inv.purchase_price
            if cost > 0:
                resp.roi_percent = float((inv.quantity * inv.current_price - cost) / cost * 100)
        return resp

    def _bond_to_response(self, bond: PolishBond) -> PolishBondResponse:
        nominal = Decimal(bond.quantity) * Decimal("100")
        today = date.today()
        days_held = (today - bond.purchase_date).days
        accrued = nominal * bond.first_period_rate * Decimal(days_held) / Decimal("365")
        current_value = nominal + accrued

        return PolishBondResponse(
            id=bond.id,
            bond_type=bond.bond_type,
            series=bond.series,
            quantity=bond.quantity,
            purchase_date=bond.purchase_date,
            maturity_date=bond.maturity_date,
            first_period_rate=bond.first_period_rate,
            current_value=current_value,
            nominal_value=nominal,
            accrued_interest=accrued,
            is_active=bond.is_active,
            notes=bond.notes,
        )
