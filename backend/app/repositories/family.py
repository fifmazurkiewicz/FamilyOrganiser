from typing import List
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.family import FamilyGroup, FamilyMembership, FamilyRole, InvitationLink
from app.repositories.base import BaseRepository


class FamilyGroupRepository(BaseRepository[FamilyGroup]):
    model = FamilyGroup


class FamilyMembershipRepository(BaseRepository[FamilyMembership]):
    model = FamilyMembership

    async def get_membership(
        self, user_id: UUID, group_id: UUID
    ) -> FamilyMembership | None:
        result = await self._session.execute(
            select(FamilyMembership).where(
                FamilyMembership.user_id == user_id,
                FamilyMembership.family_group_id == group_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: UUID) -> List[FamilyMembership]:
        result = await self._session.execute(
            select(FamilyMembership).where(FamilyMembership.user_id == user_id)
        )
        return list(result.scalars().all())

    async def list_by_group(self, group_id: UUID) -> List[FamilyMembership]:
        result = await self._session.execute(
            select(FamilyMembership).where(FamilyMembership.family_group_id == group_id)
        )
        return list(result.scalars().all())

    async def member_count(self, group_id: UUID) -> int:
        result = await self._session.execute(
            select(func.count()).where(FamilyMembership.family_group_id == group_id)
        )
        return result.scalar() or 0


class InvitationLinkRepository(BaseRepository[InvitationLink]):
    model = InvitationLink

    async def get_by_token(self, token: str) -> InvitationLink | None:
        result = await self._session.execute(
            select(InvitationLink).where(InvitationLink.token == token)
        )
        return result.scalar_one_or_none()

    async def list_by_group(self, group_id: UUID) -> List[InvitationLink]:
        result = await self._session.execute(
            select(InvitationLink).where(
                InvitationLink.family_group_id == group_id,
                InvitationLink.is_active == True,
            )
        )
        return list(result.scalars().all())
