from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account, JointAccountOwner
from app.repositories.base import BaseRepository


class AccountRepository(BaseRepository[Account]):
    model = Account

    async def list_by_owner(self, owner_id: UUID) -> list[Account]:
        result = await self._session.execute(
            select(Account).where(
                Account.owner_id == owner_id,
                Account.is_active == True,
            )
        )
        return list(result.scalars().all())

    async def get_joint_ownership(
        self, account_id: UUID, user_id: UUID
    ) -> JointAccountOwner | None:
        result = await self._session.execute(
            select(JointAccountOwner).where(
                JointAccountOwner.account_id == account_id,
                JointAccountOwner.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_joint_accounts(self, user_id: UUID) -> list[JointAccountOwner]:
        result = await self._session.execute(
            select(JointAccountOwner).where(JointAccountOwner.user_id == user_id)
        )
        return list(result.scalars().all())
