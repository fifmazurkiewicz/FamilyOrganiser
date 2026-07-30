"""Unit tests for FamilyService — groups, invitations, join/revoke."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BusinessLogicError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
)
from app.models.family import FamilyMembership, FamilyRole, InvitationLink
from app.services.family import FamilyService


class TestCreateAndListGroups:
    async def test_create_group_makes_creator_admin(
        self, db_session: AsyncSession, test_user
    ):
        svc = FamilyService(db_session)
        group = await svc.create_group(test_user, "Kowalski")

        assert group.id is not None
        assert group.name == "Kowalski"
        membership = await svc._get_membership(test_user.id, group.id)
        assert membership is not None
        assert membership.role == FamilyRole.ADMIN

    async def test_list_user_groups(self, db_session: AsyncSession, test_user):
        svc = FamilyService(db_session)
        await svc.create_group(test_user, "Grupa A")
        await svc.create_group(test_user, "Grupa B")

        groups = await svc.list_user_groups(test_user.id)
        assert len(groups) == 2
        names = {g.name for g, _ in groups}
        assert names == {"Grupa A", "Grupa B"}
        assert all(count == 1 for _, count in groups)


class TestInvitations:
    async def test_create_invitation(self, db_session: AsyncSession, test_user):
        svc = FamilyService(db_session)
        group = await svc.create_group(test_user, "Zaproszenia")
        link = await svc.create_invitation(test_user, group.id, single_use=True, expire_days=3)

        assert link.token
        assert link.family_group_id == group.id
        assert link.single_use is True
        assert link.is_active is True
        assert link.used is False
        expires_at = link.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        assert expires_at > datetime.now(timezone.utc)

    async def test_create_invitation_requires_admin(
        self, db_session: AsyncSession, test_user, test_user2
    ):
        svc = FamilyService(db_session)
        group = await svc.create_group(test_user, "Admin only")
        # add second user as member without invitation flow
        db_session.add(
            FamilyMembership(
                user_id=test_user2.id,
                family_group_id=group.id,
                role=FamilyRole.MEMBER,
            )
        )
        await db_session.flush()

        with pytest.raises(ForbiddenError):
            await svc.create_invitation(test_user2, group.id)

    async def test_join_via_invitation_returns_family_group(
        self, db_session: AsyncSession, test_user, test_user2
    ):
        svc = FamilyService(db_session)
        group = await svc.create_group(test_user, "Dołączanie")
        link = await svc.create_invitation(test_user, group.id)

        joined = await svc.join_via_invitation(test_user2, link.token)

        assert joined.id == group.id
        assert joined.name == "Dołączanie"
        membership = await svc._get_membership(test_user2.id, group.id)
        assert membership is not None
        assert membership.role == FamilyRole.MEMBER

    async def test_join_single_use_marks_link_used(
        self, db_session: AsyncSession, test_user, test_user2
    ):
        svc = FamilyService(db_session)
        group = await svc.create_group(test_user, "Single use")
        link = await svc.create_invitation(test_user, group.id, single_use=True)

        await svc.join_via_invitation(test_user2, link.token)
        await db_session.refresh(link)

        assert link.used is True
        assert link.is_active is False

    async def test_join_invalid_token(self, db_session: AsyncSession, test_user2):
        svc = FamilyService(db_session)
        with pytest.raises(NotFoundError):
            await svc.join_via_invitation(test_user2, "nieistniejacy-token")

    async def test_join_already_member(
        self, db_session: AsyncSession, test_user, test_user2
    ):
        svc = FamilyService(db_session)
        group = await svc.create_group(test_user, "Duplikat")
        link = await svc.create_invitation(test_user, group.id, single_use=False)
        await svc.join_via_invitation(test_user2, link.token)

        with pytest.raises(ConflictError):
            await svc.join_via_invitation(test_user2, link.token)

    async def test_join_revoked_invitation(
        self, db_session: AsyncSession, test_user, test_user2
    ):
        svc = FamilyService(db_session)
        group = await svc.create_group(test_user, "Revoke")
        link = await svc.create_invitation(test_user, group.id)
        await svc.revoke_invitation(test_user, group.id, link.id)

        with pytest.raises(BusinessLogicError):
            await svc.join_via_invitation(test_user2, link.token)

    async def test_join_expired_invitation(
        self, db_session: AsyncSession, test_user, test_user2
    ):
        svc = FamilyService(db_session)
        group = await svc.create_group(test_user, "Expired")
        link = InvitationLink(
            token="expired-token-123",
            family_group_id=group.id,
            created_by_id=test_user.id,
            single_use=True,
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
            is_active=True,
        )
        db_session.add(link)
        await db_session.flush()

        with pytest.raises(BusinessLogicError):
            await svc.join_via_invitation(test_user2, link.token)

    async def test_revoke_invitation_not_found(
        self, db_session: AsyncSession, test_user
    ):
        svc = FamilyService(db_session)
        group = await svc.create_group(test_user, "Brak linku")
        with pytest.raises(NotFoundError):
            await svc.revoke_invitation(test_user, group.id, uuid.uuid4())


class TestMembers:
    async def test_remove_member(
        self, db_session: AsyncSession, test_user, test_user2
    ):
        svc = FamilyService(db_session)
        group = await svc.create_group(test_user, "Usuwanie")
        link = await svc.create_invitation(test_user, group.id, single_use=False)
        await svc.join_via_invitation(test_user2, link.token)

        await svc.remove_member(test_user, group.id, test_user2.id)
        assert await svc._get_membership(test_user2.id, group.id) is None

    async def test_transfer_admin(
        self, db_session: AsyncSession, test_user, test_user2
    ):
        svc = FamilyService(db_session)
        group = await svc.create_group(test_user, "Transfer")
        link = await svc.create_invitation(test_user, group.id, single_use=False)
        await svc.join_via_invitation(test_user2, link.token)

        await svc.transfer_admin(test_user, group.id, test_user2.id)

        old_admin = await svc._get_membership(test_user.id, group.id)
        new_admin = await svc._get_membership(test_user2.id, group.id)
        assert old_admin.role == FamilyRole.MEMBER
        assert new_admin.role == FamilyRole.ADMIN

    async def test_require_membership_forbidden(
        self, db_session: AsyncSession, test_user, test_user2
    ):
        svc = FamilyService(db_session)
        group = await svc.create_group(test_user, "Private")
        with pytest.raises(ForbiddenError):
            await svc.require_membership(test_user2.id, group.id)
