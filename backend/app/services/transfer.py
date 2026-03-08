import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, BusinessLogicError
from app.models.transfer import Transfer, TransferType
from app.models.account import Account
from app.models.savings import SavingsGoal
from app.repositories.base import BaseRepository


class TransferRepository(BaseRepository[Transfer]):
    model = Transfer

    async def list_for_user(self, user_id: uuid.UUID) -> list[Transfer]:
        result = await self.session.execute(
            select(Transfer)
            .where(Transfer.user_id == user_id)
            .order_by(Transfer.transfer_date.desc(), Transfer.created_at.desc())
        )
        return list(result.scalars().all())


class TransferService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = TransferRepository(db)

    async def list(self, user_id: uuid.UUID) -> list[Transfer]:
        return await self.repo.list_for_user(user_id)

    async def create(self, user_id: uuid.UUID, data: dict) -> Transfer:
        transfer_type = TransferType(data["transfer_type"])

        # Validate and update balances / goal amounts
        if transfer_type == TransferType.ACCOUNT_TO_ACCOUNT:
            await self._validate_account(user_id, data.get("from_account_id"))
            await self._validate_account(user_id, data.get("to_account_id"))
            await self._debit_account(data["from_account_id"], data["amount"])
            await self._credit_account(data["to_account_id"], data["amount"])

        elif transfer_type == TransferType.ACCOUNT_TO_GOAL:
            await self._validate_account(user_id, data.get("from_account_id"))
            await self._validate_goal(user_id, data.get("to_goal_id"))
            await self._debit_account(data["from_account_id"], data["amount"])
            await self._credit_goal(data["to_goal_id"], data["amount"])

        elif transfer_type == TransferType.GOAL_TO_ACCOUNT:
            await self._validate_goal(user_id, data.get("from_goal_id"))
            await self._validate_account(user_id, data.get("to_account_id"))
            await self._debit_goal(data["from_goal_id"], data["amount"])
            await self._credit_account(data["to_account_id"], data["amount"])

        elif transfer_type == TransferType.GOAL_TO_GOAL:
            await self._validate_goal(user_id, data.get("from_goal_id"))
            await self._validate_goal(user_id, data.get("to_goal_id"))
            await self._debit_goal(data["from_goal_id"], data["amount"])
            await self._credit_goal(data["to_goal_id"], data["amount"])

        transfer = Transfer(user_id=user_id, **data)
        await self.repo.add(transfer)
        await self.repo.commit()
        return transfer

    async def _validate_account(self, user_id: uuid.UUID, account_id: uuid.UUID | None) -> Account:
        if not account_id:
            raise BusinessLogicError("Account ID required")
        result = await self.db.execute(select(Account).where(Account.id == account_id))
        acc = result.scalar_one_or_none()
        if not acc:
            raise BusinessLogicError("Account not found")
        if acc.owner_id != user_id:
            raise ForbiddenError("Not your account")
        return acc

    async def _validate_goal(self, user_id: uuid.UUID, goal_id: uuid.UUID | None) -> SavingsGoal:
        if not goal_id:
            raise BusinessLogicError("Goal ID required")
        result = await self.db.execute(select(SavingsGoal).where(SavingsGoal.id == goal_id))
        goal = result.scalar_one_or_none()
        if not goal:
            raise BusinessLogicError("Goal not found")
        if goal.user_id != user_id:
            raise ForbiddenError("Not your goal")
        return goal

    async def _debit_account(self, account_id: uuid.UUID, amount) -> None:
        result = await self.db.execute(select(Account).where(Account.id == account_id))
        acc = result.scalar_one()
        acc.balance -= amount

    async def _credit_account(self, account_id: uuid.UUID, amount) -> None:
        result = await self.db.execute(select(Account).where(Account.id == account_id))
        acc = result.scalar_one()
        acc.balance += amount

    async def _debit_goal(self, goal_id: uuid.UUID, amount) -> None:
        result = await self.db.execute(select(SavingsGoal).where(SavingsGoal.id == goal_id))
        goal = result.scalar_one()
        goal.current_amount = max(goal.current_amount - amount, 0)

    async def _credit_goal(self, goal_id: uuid.UUID, amount) -> None:
        result = await self.db.execute(select(SavingsGoal).where(SavingsGoal.id == goal_id))
        goal = result.scalar_one()
        goal.current_amount += amount
