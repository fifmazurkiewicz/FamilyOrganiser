import uuid
import secrets
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.base import get_db
from app.models.user import User
from app.models.family import FamilyGroup, FamilyMembership, FamilyRole, InvitationLink
from app.models.notification import Notification, NotificationType
from app.models.audit_log import AuditLog
from app.schemas.family import (
    FamilyGroupCreate, FamilyGroupUpdate, FamilyGroupResponse,
    MembershipResponse, MemberResponse, SharingPreferencesUpdate,
    InvitationLinkCreate, InvitationLinkResponse, TransferAdminRoleRequest,
)
from app.api.deps import get_current_user
from app.core.config import settings

router = APIRouter(prefix="/groups", tags=["family"])


async def _get_membership(
    user_id: uuid.UUID, group_id: uuid.UUID, db: AsyncSession
) -> FamilyMembership:
    result = await db.execute(
        select(FamilyMembership).where(
            FamilyMembership.user_id == user_id,
            FamilyMembership.family_group_id == group_id,
        )
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this group")
    return membership


@router.post("/", response_model=FamilyGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    payload: FamilyGroupCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    group = FamilyGroup(name=payload.name)
    db.add(group)
    await db.flush()

    membership = FamilyMembership(
        user_id=current_user.id,
        family_group_id=group.id,
        role=FamilyRole.ADMIN,
    )
    db.add(membership)
    await db.commit()
    return FamilyGroupResponse(
        id=group.id, name=group.name, created_at=group.created_at, member_count=1
    )


@router.get("/", response_model=list[FamilyGroupResponse])
async def list_my_groups(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FamilyMembership).where(FamilyMembership.user_id == current_user.id)
    )
    memberships = result.scalars().all()

    groups = []
    for m in memberships:
        group_result = await db.execute(
            select(FamilyGroup).where(FamilyGroup.id == m.family_group_id)
        )
        group = group_result.scalar_one_or_none()
        if group:
            count_result = await db.execute(
                select(func.count()).where(FamilyMembership.family_group_id == group.id)
            )
            count = count_result.scalar() or 0
            groups.append(
                FamilyGroupResponse(
                    id=group.id, name=group.name, created_at=group.created_at,
                    member_count=count
                )
            )
    return groups


@router.get("/{group_id}/members", response_model=list[MemberResponse])
async def list_members(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_membership(current_user.id, group_id, db)
    result = await db.execute(
        select(FamilyMembership).where(FamilyMembership.family_group_id == group_id)
    )
    memberships = result.scalars().all()
    members = []
    for m in memberships:
        user_result = await db.execute(select(User).where(User.id == m.user_id))
        user = user_result.scalar_one_or_none()
        if user:
            members.append(MemberResponse(
                id=m.id,
                user_id=m.user_id,
                full_name=user.full_name,
                email=user.email,
                avatar_url=user.avatar_url,
                role=m.role,
                joined_at=m.joined_at,
            ))
    return members


@router.delete("/{group_id}/members/{member_user_id}")
async def remove_member(
    group_id: uuid.UUID,
    member_user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    my_membership = await _get_membership(current_user.id, group_id, db)
    if my_membership.role != FamilyRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only family admin can remove members")

    target_result = await db.execute(
        select(FamilyMembership).where(
            FamilyMembership.user_id == member_user_id,
            FamilyMembership.family_group_id == group_id,
        )
    )
    target_membership = target_result.scalar_one_or_none()
    if not target_membership:
        raise HTTPException(status_code=404, detail="Member not found")

    group_result = await db.execute(select(FamilyGroup).where(FamilyGroup.id == group_id))
    group = group_result.scalar_one_or_none()

    await db.delete(target_membership)

    # Notify removed user
    notification = Notification(
        user_id=member_user_id,
        notification_type=NotificationType.GROUP_REMOVED,
        title="Usunięty z grupy",
        body=f"Zostałeś usunięty z grupy {group.name if group else ''}.",
    )
    db.add(notification)
    await db.commit()
    return {"message": "Member removed"}


@router.post("/{group_id}/transfer-admin")
async def transfer_admin(
    group_id: uuid.UUID,
    payload: TransferAdminRoleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    my_membership = await _get_membership(current_user.id, group_id, db)
    if my_membership.role != FamilyRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only family admin can transfer role")

    target_result = await db.execute(
        select(FamilyMembership).where(
            FamilyMembership.user_id == payload.new_admin_user_id,
            FamilyMembership.family_group_id == group_id,
        )
    )
    target = target_result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="Target member not found")

    my_membership.role = FamilyRole.MEMBER
    target.role = FamilyRole.ADMIN

    log = AuditLog(
        actor_id=current_user.id,
        target_user_id=payload.new_admin_user_id,
        family_group_id=group_id,
        action="transfer_admin_role",
    )
    db.add(log)
    await db.commit()
    return {"message": "Admin role transferred"}


@router.patch("/{group_id}/sharing", response_model=MembershipResponse)
async def update_sharing(
    group_id: uuid.UUID,
    payload: SharingPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    membership = await _get_membership(current_user.id, group_id, db)
    if payload.share_expenses is not None:
        membership.share_expenses = payload.share_expenses
    if payload.share_investments is not None:
        membership.share_investments = payload.share_investments
    if payload.share_savings is not None:
        membership.share_savings = payload.share_savings
    if payload.share_budget is not None:
        membership.share_budget = payload.share_budget
    await db.commit()
    await db.refresh(membership)
    return membership


@router.post("/{group_id}/invitations", response_model=InvitationLinkResponse)
async def create_invitation(
    group_id: uuid.UUID,
    payload: InvitationLinkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    my_membership = await _get_membership(current_user.id, group_id, db)
    if my_membership.role != FamilyRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only family admin can create invitations")

    # Check member count
    count_result = await db.execute(
        select(func.count()).where(FamilyMembership.family_group_id == group_id)
    )
    count = count_result.scalar() or 0
    if count >= settings.MAX_FAMILY_GROUP_MEMBERS:
        raise HTTPException(status_code=400, detail="Group member limit reached (max 20)")

    token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(days=payload.expire_days)
    link = InvitationLink(
        token=token,
        family_group_id=group_id,
        created_by_id=current_user.id,
        single_use=payload.single_use,
        expires_at=expires,
    )
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link


@router.post("/join/{token}")
async def join_group(
    token: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InvitationLink).where(InvitationLink.token == token)
    )
    link = result.scalar_one_or_none()
    if not link or not link.is_active:
        raise HTTPException(status_code=400, detail="Invalid or expired invitation link")
    if link.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invitation link has expired")
    if link.single_use and link.used:
        raise HTTPException(status_code=400, detail="Invitation link already used")

    # Check member count
    count_result = await db.execute(
        select(func.count()).where(FamilyMembership.family_group_id == link.family_group_id)
    )
    count = count_result.scalar() or 0
    if count >= settings.MAX_FAMILY_GROUP_MEMBERS:
        raise HTTPException(status_code=400, detail="Group is full (max 20 members)")

    # Check if already a member
    existing = await db.execute(
        select(FamilyMembership).where(
            FamilyMembership.user_id == current_user.id,
            FamilyMembership.family_group_id == link.family_group_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already a member of this group")

    membership = FamilyMembership(
        user_id=current_user.id,
        family_group_id=link.family_group_id,
        role=FamilyRole.MEMBER,
    )
    db.add(membership)

    if link.single_use:
        link.used = True
        link.is_active = False

    await db.commit()
    return {"message": "Joined group successfully"}


@router.delete("/{group_id}/invitations/{link_id}")
async def revoke_invitation(
    group_id: uuid.UUID,
    link_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    my_membership = await _get_membership(current_user.id, group_id, db)
    if my_membership.role != FamilyRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only family admin can revoke invitations")

    result = await db.execute(
        select(InvitationLink).where(
            InvitationLink.id == link_id,
            InvitationLink.family_group_id == group_id,
        )
    )
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Invitation not found")

    link.is_active = False
    await db.commit()
    return {"message": "Invitation revoked"}


@router.post("/{group_id}/admin/reset-password")
async def family_admin_reset_password(
    group_id: uuid.UUID,
    target_user_id: uuid.UUID,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.core.security import hash_password
    my_membership = await _get_membership(current_user.id, group_id, db)
    if my_membership.role != FamilyRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only family admin can reset passwords")

    # Verify target is in group
    await _get_membership(target_user_id, group_id, db)

    user_result = await db.execute(select(User).where(User.id == target_user_id))
    target = user_result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    target.hashed_password = hash_password(new_password)

    notification = Notification(
        user_id=target.id,
        notification_type=NotificationType.PASSWORD_RESET,
        title="Hasło zostało zmienione",
        body=f"Twoje hasło zostało zmienione przez administratora grupy.",
    )
    db.add(notification)

    log = AuditLog(
        actor_id=current_user.id,
        target_user_id=target.id,
        family_group_id=group_id,
        action="family_admin_password_reset",
        resource_type="user",
        resource_id=str(target.id),
    )
    db.add(log)
    await db.commit()
    return {"message": "Password reset successfully"}
