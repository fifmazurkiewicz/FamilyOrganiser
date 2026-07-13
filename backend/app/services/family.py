"""Family group management service."""
import secrets
from datetime import datetime, timedelta, timezone
from typing import List, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    BusinessLogicError,
    ConflictError,
    ForbiddenError,
    GroupLimitExceededError,
    NotFoundError,
)
from app.models.audit_log import AuditLog
from app.models.family import FamilyGroup, FamilyMembership, FamilyRole, InvitationLink
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.repositories.family import (
    FamilyGroupRepository,
    FamilyMembershipRepository,
    InvitationLinkRepository,
)


class FamilyService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._groups = FamilyGroupRepository(session)
        self._memberships = FamilyMembershipRepository(session)
        self._invitations = InvitationLinkRepository(session)

    # ------------------------------------------------------------------ groups

    async def create_group(self, creator: User, name: str) -> FamilyGroup:
        group = FamilyGroup(name=name)
        self._session.add(group)
        await self._session.flush()

        membership = FamilyMembership(
            user_id=creator.id,
            family_group_id=group.id,
            role=FamilyRole.ADMIN,
        )
        self._session.add(membership)
        await self._session.commit()
        await self._session.refresh(group)
        return group

    async def list_user_groups(self, user_id: UUID) -> List[Tuple[FamilyGroup, int]]:
        return await self._groups.list_with_member_counts(user_id)

    async def admin_list_all_groups(self) -> List[Tuple[FamilyGroup, int]]:
        return await self._groups.list_with_member_counts()

    async def admin_delete_group(self, group_id: UUID) -> None:
        group = await self._groups.get(group_id)
        if not group:
            raise NotFoundError("Group not found")
        await self._session.delete(group)
        await self._session.commit()

    # --------------------------------------------------------------- members

    async def require_membership(
        self, user_id: UUID, group_id: UUID
    ) -> FamilyMembership:
        membership = await self._memberships.get_membership(user_id, group_id)
        if not membership:
            raise ForbiddenError("Not a member of this family group")
        return membership

    async def require_admin(self, user_id: UUID, group_id: UUID) -> FamilyMembership:
        membership = await self.require_membership(user_id, group_id)
        if membership.role != FamilyRole.ADMIN:
            raise ForbiddenError("Family admin role required")
        return membership

    async def list_members_with_users(
        self, group_id: UUID
    ) -> List[Tuple[FamilyMembership, User]]:
        return await self._memberships.list_by_group_with_users(group_id)

    async def remove_member(
        self, actor: User, group_id: UUID, target_user_id: UUID
    ) -> None:
        await self.require_admin(actor.id, group_id)

        target = await self._memberships.get_membership(target_user_id, group_id)
        if not target:
            raise NotFoundError("Member not found in this group")

        group = await self._groups.get(group_id)
        await self._session.delete(target)

        notif = Notification(
            user_id=target_user_id,
            notification_type=NotificationType.GROUP_REMOVED,
            title="Usunięty z grupy rodzinnej",
            body=f"Zostałeś usunięty z grupy \"{group.name if group else ''}.\"",
        )
        self._session.add(notif)
        await self._session.commit()

    async def transfer_admin(
        self, actor: User, group_id: UUID, new_admin_id: UUID
    ) -> None:
        my_membership = await self.require_admin(actor.id, group_id)

        target = await self._memberships.get_membership(new_admin_id, group_id)
        if not target:
            raise NotFoundError("Target member not found in this group")

        my_membership.role = FamilyRole.MEMBER
        target.role = FamilyRole.ADMIN

        self._session.add(
            AuditLog(
                actor_id=actor.id,
                target_user_id=new_admin_id,
                family_group_id=group_id,
                action="transfer_admin_role",
            )
        )
        await self._session.commit()

    async def update_sharing(
        self,
        user: User,
        group_id: UUID,
        *,
        share_expenses: bool | None = None,
        share_investments: bool | None = None,
        share_savings: bool | None = None,
        share_budget: bool | None = None,
    ) -> FamilyMembership:
        membership = await self.require_membership(user.id, group_id)
        if share_expenses is not None:
            membership.share_expenses = share_expenses
        if share_investments is not None:
            membership.share_investments = share_investments
        if share_savings is not None:
            membership.share_savings = share_savings
        if share_budget is not None:
            membership.share_budget = share_budget
        await self._session.commit()
        await self._session.refresh(membership)
        return membership

    # ----------------------------------------------------------- invitations

    async def create_invitation(
        self,
        actor: User,
        group_id: UUID,
        single_use: bool = True,
        expire_days: int = 7,
    ) -> InvitationLink:
        await self.require_admin(actor.id, group_id)
        count = await self._memberships.member_count(group_id)
        if count >= settings.MAX_FAMILY_GROUP_MEMBERS:
            raise GroupLimitExceededError()

        token = secrets.token_urlsafe(32)
        expires = datetime.now(timezone.utc) + timedelta(days=expire_days)
        link = InvitationLink(
            token=token,
            family_group_id=group_id,
            created_by_id=actor.id,
            single_use=single_use,
            expires_at=expires,
        )
        self._session.add(link)
        await self._session.commit()
        await self._session.refresh(link)
        return link

    async def join_via_invitation(self, user: User, token: str) -> FamilyGroup:
        link = await self._invitations.get_by_token(token)
        if not link or not link.is_active:
            raise BusinessLogicError("Invalid or revoked invitation link")
        if link.expires_at < datetime.now(timezone.utc):
            raise BusinessLogicError("Invitation link has expired")
        if link.single_use and link.used:
            raise BusinessLogicError("This invitation link has already been used")

        count = await self._memberships.member_count(link.family_group_id)
        if count >= settings.MAX_FAMILY_GROUP_MEMBERS:
            raise GroupLimitExceededError()

        existing = await self._memberships.get_membership(user.id, link.family_group_id)
        if existing:
            raise ConflictError("Already a member of this family group")

        self._session.add(
            FamilyMembership(
                user_id=user.id,
                family_group_id=link.family_group_id,
                role=FamilyRole.MEMBER,
            )
        )

        if link.single_use:
            link.used = True
            link.is_active = False

        await self._session.commit()

        group = await self._groups.get(link.family_group_id)
        if not group:
            raise NotFoundError("Group not found")
        return group

    async def revoke_invitation(
        self, actor: User, group_id: UUID, link_id: UUID
    ) -> None:
        await self.require_admin(actor.id, group_id)
        link = await self._invitations.get(link_id)
        if not link or link.family_group_id != group_id:
            raise NotFoundError("Invitation not found")
        link.is_active = False
        await self._session.commit()

    async def admin_reset_member_password(
        self,
        actor: User,
        group_id: UUID,
        target_user_id: UUID,
        new_password: str,
    ) -> None:
        from app.core.security import hash_password
        from app.repositories.user import UserRepository

        await self.require_admin(actor.id, group_id)
        await self.require_membership(target_user_id, group_id)

        user_repo = UserRepository(self._session)
        target = await user_repo.get(target_user_id)
        if not target:
            raise NotFoundError("User not found")

        target.hashed_password = hash_password(new_password)

        self._session.add(
            Notification(
                user_id=target.id,
                notification_type=NotificationType.PASSWORD_RESET,
                title="Hasło zostało zmienione",
                body="Twoje hasło zostało zmienione przez administratora grupy rodzinnej.",
            )
        )
        self._session.add(
            AuditLog(
                actor_id=actor.id,
                target_user_id=target.id,
                family_group_id=group_id,
                action="family_admin_password_reset",
                resource_type="user",
                resource_id=str(target.id),
            )
        )
        await self._session.commit()
