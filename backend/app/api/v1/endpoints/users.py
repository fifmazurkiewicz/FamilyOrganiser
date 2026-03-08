import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_app_admin, get_current_user
from app.db.base import get_db
from app.models.family import FamilyMembership, FamilyRole
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.default_currency is not None:
        current_user.default_currency = payload.default_currency
    if payload.avatar_url is not None:
        current_user.avatar_url = payload.avatar_url
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.delete("/me", status_code=204)
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.core.exceptions import BusinessLogicError

    result = await db.execute(
        select(FamilyMembership).where(
            FamilyMembership.user_id == current_user.id,
            FamilyMembership.role == FamilyRole.ADMIN,
        )
    )
    if result.scalars().first():
        raise BusinessLogicError(
            "Transfer admin role in all groups before deleting your account"
        )
    current_user.is_active = False
    await db.commit()


@router.get("/", response_model=list[UserResponse], tags=["Admin"])
async def list_users(
    admin: User = Depends(get_current_app_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User))
    return result.scalars().all()


@router.post("/{user_id}/lock", tags=["Admin"])
async def lock_user(
    user_id: uuid.UUID,
    admin: User = Depends(get_current_app_admin),
    db: AsyncSession = Depends(get_db),
):
    from app.core.exceptions import NotFoundError

    user = await db.get(User, user_id)
    if not user:
        raise NotFoundError("User not found")
    user.is_locked = True
    await db.commit()
    return {"message": "User locked"}


@router.post("/{user_id}/unlock", tags=["Admin"])
async def unlock_user(
    user_id: uuid.UUID,
    admin: User = Depends(get_current_app_admin),
    db: AsyncSession = Depends(get_db),
):
    from app.core.exceptions import NotFoundError

    user = await db.get(User, user_id)
    if not user:
        raise NotFoundError("User not found")
    user.is_locked = False
    user.security_question_attempts = 0
    await db.commit()
    return {"message": "User unlocked"}
