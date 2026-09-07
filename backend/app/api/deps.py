from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.models.family import FamilyMembership, FamilyRole
from app.services.user_provisioning import get_or_create_user_from_claims
import uuid

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload, mode = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    if mode == "supabase":
        user = await get_or_create_user_from_claims(db, payload)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
    else:
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
        result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

    if not user.is_active or user.is_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is locked or inactive",
        )
    return user


async def require_approved(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="account_pending_approval",
        )
    return current_user


async def get_current_app_admin(current_user: User = Depends(require_approved)) -> User:
    if not current_user.is_app_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="App admin required")
    return current_user


async def get_family_admin(
    group_id: uuid.UUID,
    current_user: User = Depends(require_approved),
    db: AsyncSession = Depends(get_db),
) -> tuple[User, FamilyMembership]:
    result = await db.execute(
        select(FamilyMembership).where(
            FamilyMembership.user_id == current_user.id,
            FamilyMembership.family_group_id == group_id,
        )
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this group")
    if membership.role != FamilyRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Family admin required")
    return current_user, membership
