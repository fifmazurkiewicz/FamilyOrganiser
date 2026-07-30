"""Shared family-group membership checks for product modules."""
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.family import FamilyMembership
from app.services.family import FamilyService


async def require_family_member(
    session: AsyncSession, user_id: UUID, family_group_id: UUID
) -> FamilyMembership:
    return await FamilyService(session).require_membership(user_id, family_group_id)
