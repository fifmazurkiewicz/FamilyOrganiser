import uuid
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

import httpx
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_app_admin, get_current_user, require_approved
from app.core.config import settings
from app.db.base import get_db
from app.models.family import FamilyMembership, FamilyRole
from app.models.monthly_budget import BudgetEntry
from app.models.notification import Notification
from app.models.shopping import ShoppingItem, ShoppingList
from app.models.simple_investment import SimpleInvestment
from app.models.task import TaskItem, TaskList
from app.models.user import SecurityQuestion, User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


def _json_value(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (uuid.UUID, Decimal)):
        return str(value)
    return value


def _row_dict(instance) -> dict:
    return {
        column.name: _json_value(getattr(instance, column.name))
        for column in instance.__table__.columns
    }


async def _all(db: AsyncSession, model, *criteria):
    result = await db.execute(select(model).where(*criteria))
    return [_row_dict(row) for row in result.scalars().all()]


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    payload: UserUpdate,
    current_user: User = Depends(require_approved),
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


@router.get("/me/export")
async def export_my_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export data directly connected to the authenticated user as JSON."""
    user_id = current_user.id
    payload = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "account": {
            "id": str(current_user.id),
            "email": current_user.email,
            "full_name": current_user.full_name,
            "avatar_url": current_user.avatar_url,
            "default_currency": current_user.default_currency,
            "created_at": current_user.created_at.isoformat(),
        },
        "memberships": await _all(db, FamilyMembership, FamilyMembership.user_id == user_id),
        "investments": await _all(db, SimpleInvestment, SimpleInvestment.user_id == user_id),
        "notifications": await _all(db, Notification, Notification.user_id == user_id),
        "budget_entries_created": await _all(db, BudgetEntry, BudgetEntry.created_by == user_id),
        "shopping_lists_created": await _all(db, ShoppingList, ShoppingList.created_by == user_id),
        "shopping_items_added": await _all(db, ShoppingItem, ShoppingItem.added_by == user_id),
        "shopping_items_bought": await _all(db, ShoppingItem, ShoppingItem.bought_by == user_id),
        "task_lists_created": await _all(db, TaskList, TaskList.created_by == user_id),
        "tasks_assigned": await _all(db, TaskItem, TaskItem.assigned_to == user_id),
        "tasks_completed": await _all(db, TaskItem, TaskItem.done_by == user_id),
    }
    response = JSONResponse(payload)
    response.headers["Content-Disposition"] = (
        f'attachment; filename="familyorganiser-data-{user_id}.json"'
    )
    return response


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
    if current_user.supabase_auth_id:
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            raise HTTPException(status_code=503, detail="account_deletion_not_configured")
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.delete(
                f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/admin/users/{current_user.supabase_auth_id}",
                headers={
                    "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
                    "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
                },
            )
        if response.status_code not in (200, 204, 404):
            raise HTTPException(status_code=502, detail="identity_deletion_failed")

    user_id = current_user.id
    await db.execute(delete(Notification).where(Notification.user_id == user_id))
    await db.execute(delete(SimpleInvestment).where(SimpleInvestment.user_id == user_id))
    await db.execute(delete(FamilyMembership).where(FamilyMembership.user_id == user_id))
    await db.execute(delete(SecurityQuestion).where(SecurityQuestion.user_id == user_id))

    # Preserve shared records by retaining only an anonymous foreign-key anchor.
    current_user.email = f"deleted-{user_id}@invalid.local"
    current_user.full_name = "Usunięty użytkownik"
    current_user.hashed_password = None
    current_user.supabase_auth_id = None
    current_user.avatar_url = None
    current_user.is_active = False
    current_user.is_approved = False
    current_user.is_locked = True
    await db.commit()
    return Response(status_code=204)


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


@router.delete("/{user_id}", status_code=204, tags=["Admin"])
async def admin_delete_user(
    user_id: uuid.UUID,
    admin: User = Depends(get_current_app_admin),
    db: AsyncSession = Depends(get_db),
):
    from app.core.exceptions import BusinessLogicError, NotFoundError

    if user_id == admin.id:
        raise BusinessLogicError("Cannot delete your own account")
    user = await db.get(User, user_id)
    if not user:
        raise NotFoundError("User not found")
    user.is_active = False
    await db.commit()


@router.post("/{user_id}/approve", tags=["Admin"])
async def approve_user(
    user_id: uuid.UUID,
    admin: User = Depends(get_current_app_admin),
    db: AsyncSession = Depends(get_db),
):
    from app.core.exceptions import NotFoundError

    user = await db.get(User, user_id)
    if not user:
        raise NotFoundError("User not found")
    user.is_approved = True
    await db.commit()
    return {"message": "User approved"}


@router.post("/{user_id}/revoke", tags=["Admin"])
async def revoke_user(
    user_id: uuid.UUID,
    admin: User = Depends(get_current_app_admin),
    db: AsyncSession = Depends(get_db),
):
    from app.core.exceptions import BusinessLogicError, NotFoundError

    if user_id == admin.id:
        raise BusinessLogicError("Cannot revoke your own access")
    user = await db.get(User, user_id)
    if not user:
        raise NotFoundError("User not found")
    user.is_approved = False
    await db.commit()
    return {"message": "User access revoked"}
