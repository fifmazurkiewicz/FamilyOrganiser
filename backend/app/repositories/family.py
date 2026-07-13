from typing import List, Tuple
from uuid import UUID

from sqlalchemy import func, select

from app.models.family import FamilyGroup, FamilyMembership, InvitationLink
from app.models.user import User
from app.repositories.base import BaseRepository


class FamilyGroupRepository(BaseRepository[FamilyGroup]):
    model = FamilyGroup

    async def list_with_member_counts(
        self, user_id: UUID | None = None
    ) -> List[Tuple[FamilyGroup, int]]:
        """Grupy wraz z liczbą członków w jednym zapytaniu.

        Gdy podano user_id — tylko grupy, do których należy użytkownik;
        w przeciwnym razie wszystkie grupy (widok administratora).
        """
        counts = (
            select(
                FamilyMembership.family_group_id,
                func.count().label("member_count"),
            )
            .group_by(FamilyMembership.family_group_id)
            .subquery()
        )
        stmt = (
            select(FamilyGroup, func.coalesce(counts.c.member_count, 0))
            .join(counts, counts.c.family_group_id == FamilyGroup.id, isouter=True)
            .order_by(FamilyGroup.created_at.desc())
        )
        if user_id is not None:
            stmt = stmt.join(
                FamilyMembership, FamilyMembership.family_group_id == FamilyGroup.id
            ).where(FamilyMembership.user_id == user_id)
        result = await self._session.execute(stmt)
        return [(group, count) for group, count in result.all()]


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

    async def list_by_group_with_users(
        self, group_id: UUID
    ) -> List[Tuple[FamilyMembership, User]]:
        result = await self._session.execute(
            select(FamilyMembership, User)
            .join(User, User.id == FamilyMembership.user_id)
            .where(FamilyMembership.family_group_id == group_id)
        )
        return [(membership, user) for membership, user in result.all()]

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
