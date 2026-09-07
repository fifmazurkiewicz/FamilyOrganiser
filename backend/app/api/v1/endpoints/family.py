import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_app_admin, get_current_user, require_approved
from app.db.base import get_db
from app.models.user import User
from app.schemas.family import (
    FamilyGroupCreate,
    FamilyGroupResponse,
    InvitationLinkCreate,
    InvitationLinkResponse,
    MemberResponse,
    MembershipResponse,
    SharingPreferencesUpdate,
    TransferAdminRoleRequest,
)
from app.services.family import FamilyService

router = APIRouter(
    prefix="/groups",
    tags=["Family Groups"],
    dependencies=[Depends(require_approved)],
)


@router.post("/", response_model=FamilyGroupResponse, status_code=201)
async def create_group(
    payload: FamilyGroupCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = FamilyService(db)
    group = await svc.create_group(current_user, payload.name)
    return FamilyGroupResponse(id=group.id, name=group.name, created_at=group.created_at, member_count=1)


@router.get("/", response_model=list[FamilyGroupResponse])
async def list_groups(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = FamilyService(db)
    groups = await svc.list_user_groups(current_user.id)
    return [
        FamilyGroupResponse(id=g.id, name=g.name, created_at=g.created_at, member_count=count)
        for g, count in groups
    ]


@router.get("/{group_id}/members", response_model=list[MemberResponse])
async def list_members(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    from app.models.user import User as UserModel

    svc = FamilyService(db)
    await svc.require_membership(current_user.id, group_id)
    memberships = await svc.list_members(group_id)

    members = []
    for m in memberships:
        result = await db.execute(select(UserModel).where(UserModel.id == m.user_id))
        user = result.scalar_one_or_none()
        if user:
            members.append(
                MemberResponse(
                    id=m.id,
                    user_id=m.user_id,
                    full_name=user.full_name,
                    email=user.email,
                    avatar_url=user.avatar_url,
                    role=m.role,
                    joined_at=m.joined_at,
                )
            )
    return members


@router.delete("/{group_id}/members/{member_user_id}", status_code=204)
async def remove_member(
    group_id: uuid.UUID,
    member_user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = FamilyService(db)
    await svc.remove_member(current_user, group_id, member_user_id)


@router.post("/{group_id}/transfer-admin")
async def transfer_admin(
    group_id: uuid.UUID,
    payload: TransferAdminRoleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = FamilyService(db)
    await svc.transfer_admin(current_user, group_id, payload.new_admin_user_id)
    return {"message": "Admin role transferred"}


@router.patch("/{group_id}/sharing", response_model=MembershipResponse)
async def update_sharing(
    group_id: uuid.UUID,
    payload: SharingPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = FamilyService(db)
    return await svc.update_sharing(
        current_user,
        group_id,
        share_expenses=payload.share_expenses,
        share_investments=payload.share_investments,
        share_savings=payload.share_savings,
        share_budget=payload.share_budget,
    )


@router.post("/{group_id}/invitations", response_model=InvitationLinkResponse, status_code=201)
async def create_invitation(
    group_id: uuid.UUID,
    payload: InvitationLinkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = FamilyService(db)
    return await svc.create_invitation(
        current_user, group_id, single_use=payload.single_use, expire_days=payload.expire_days
    )


@router.post("/join/{token}")
async def join_group(
    token: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = FamilyService(db)
    group = await svc.join_via_invitation(current_user, token)
    return {"message": f"Joined group '{group.name}' successfully"}


@router.delete("/{group_id}/invitations/{link_id}", status_code=204)
async def revoke_invitation(
    group_id: uuid.UUID,
    link_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = FamilyService(db)
    await svc.revoke_invitation(current_user, group_id, link_id)


@router.get("/admin/all", response_model=list[FamilyGroupResponse])
async def admin_list_all_groups(
    admin: User = Depends(get_current_app_admin),
    db: AsyncSession = Depends(get_db),
):
    svc = FamilyService(db)
    groups_with_count = await svc.admin_list_all_groups()
    return [
        FamilyGroupResponse(id=g.id, name=g.name, created_at=g.created_at, member_count=count)
        for g, count in groups_with_count
    ]


@router.delete("/admin/{group_id}", status_code=204)
async def admin_delete_group(
    group_id: uuid.UUID,
    admin: User = Depends(get_current_app_admin),
    db: AsyncSession = Depends(get_db),
):
    svc = FamilyService(db)
    await svc.admin_delete_group(group_id)


@router.post("/{group_id}/admin/reset-password")
async def family_admin_reset_password(
    group_id: uuid.UUID,
    target_user_id: uuid.UUID,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = FamilyService(db)
    await svc.admin_reset_member_password(current_user, group_id, target_user_id, new_password)
    return {"message": "Password reset successfully"}
