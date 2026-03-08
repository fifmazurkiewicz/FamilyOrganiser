import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError
from app.models.income import Income, IncomeTemplate
from app.repositories.income import IncomeRepository, IncomeTemplateRepository
from app.schemas.income import (
    IncomeCreate, IncomeUpdate, IncomeResponse,
    IncomeTemplateCreate, IncomeTemplateResponse,
)


class IncomeService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = IncomeRepository(db)
        self.template_repo = IncomeTemplateRepository(db)

    # --- Templates ---

    async def list_templates(self, user_id: uuid.UUID) -> list[IncomeTemplateResponse]:
        templates = await self.template_repo.list_for_user(user_id)
        return [IncomeTemplateResponse.model_validate(t) for t in templates]

    async def create_template(self, user_id: uuid.UUID, data: IncomeTemplateCreate) -> IncomeTemplateResponse:
        tmpl = IncomeTemplate(user_id=user_id, **data.model_dump())
        await self.template_repo.add(tmpl)
        await self.template_repo.commit()
        return IncomeTemplateResponse.model_validate(tmpl)

    async def delete_template(self, user_id: uuid.UUID, template_id: uuid.UUID) -> None:
        tmpl = await self.template_repo.get_or_raise(template_id)
        if tmpl.user_id != user_id:
            raise ForbiddenError("Access denied")
        tmpl.is_active = False
        await self.template_repo.commit()

    # --- Incomes ---

    async def list(self, user_id: uuid.UUID, year: int | None = None, month: int | None = None) -> list[IncomeResponse]:
        incomes = await self.repo.list_for_user(user_id, year=year, month=month)
        return [IncomeResponse.model_validate(i) for i in incomes]

    async def create(self, user_id: uuid.UUID, data: IncomeCreate) -> IncomeResponse:
        is_modified = False
        if data.template_id and data.base_amount:
            is_modified = data.amount != data.base_amount

        income = Income(
            user_id=user_id,
            is_modified=is_modified,
            **data.model_dump(),
        )
        await self.repo.add(income)
        await self.repo.commit()
        return IncomeResponse.model_validate(income)

    async def update(self, user_id: uuid.UUID, income_id: uuid.UUID, data: IncomeUpdate) -> IncomeResponse:
        income = await self.repo.get_or_raise(income_id)
        if income.user_id != user_id:
            raise ForbiddenError("Access denied")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(income, field, value)
        if income.base_amount and income.amount != income.base_amount:
            income.is_modified = True
        await self.repo.commit()
        return IncomeResponse.model_validate(income)

    async def delete(self, user_id: uuid.UUID, income_id: uuid.UUID) -> None:
        income = await self.repo.get_or_raise(income_id)
        if income.user_id != user_id:
            raise ForbiddenError("Access denied")
        await self.repo.delete(income)
        await self.repo.commit()
