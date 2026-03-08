from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta

from app.db.base import get_db
from app.core.security import (
    hash_password, verify_password, hash_security_answer, verify_security_answer,
    create_access_token, create_refresh_token, decode_token
)
from app.core.config import settings
from app.models.user import User, SecurityQuestion
from app.models.audit_log import AuditLog
from app.models.notification import Notification, NotificationType
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse, RefreshRequest,
    PasswordChangeRequest, SecurityQuestionResetRequest, SecurityQuestionResponse,
    AdminPasswordResetRequest
)
from app.api.deps import get_current_user, get_current_app_admin

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        default_currency=payload.default_currency,
    )
    db.add(user)
    await db.flush()

    security_q = SecurityQuestion(
        user_id=user.id,
        question=payload.security_question,
        hashed_answer=hash_security_answer(payload.security_answer),
    )
    db.add(security_q)
    await db.commit()

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if user.is_locked:
        raise HTTPException(status_code=403, detail="Account is locked. Contact an admin.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    data = decode_token(payload.refresh_token)
    if not data or data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    import uuid
    user_id = data.get("sub")
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user or not user.is_active or user.is_locked:
        raise HTTPException(status_code=401, detail="User unavailable")

    access_token = create_access_token({"sub": str(user.id)})
    new_refresh = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(access_token=access_token, refresh_token=new_refresh)


@router.get("/security-question", response_model=SecurityQuestionResponse)
async def get_security_question(email: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(select(SecurityQuestion).where(SecurityQuestion.user_id == user.id))
    sq = result.scalar_one_or_none()
    if not sq:
        raise HTTPException(status_code=404, detail="No security question set")
    return SecurityQuestionResponse(question=sq.question)


@router.post("/reset-password/security-question")
async def reset_password_via_security_question(
    payload: SecurityQuestionResetRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_locked:
        raise HTTPException(status_code=403, detail="Account locked. Contact admin.")

    result = await db.execute(select(SecurityQuestion).where(SecurityQuestion.user_id == user.id))
    sq = result.scalar_one_or_none()
    if not sq:
        raise HTTPException(status_code=400, detail="No security question set")

    if not verify_security_answer(payload.answer, sq.hashed_answer):
        user.security_question_attempts += 1
        if user.security_question_attempts >= settings.MAX_SECURITY_QUESTION_ATTEMPTS:
            user.is_locked = True
            await db.commit()
            raise HTTPException(status_code=403, detail="Too many failed attempts. Account locked.")
        await db.commit()
        raise HTTPException(status_code=400, detail="Incorrect answer")

    user.hashed_password = hash_password(payload.new_password)
    user.security_question_attempts = 0
    await db.commit()
    return {"message": "Password reset successfully"}


@router.post("/change-password")
async def change_password(
    payload: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    current_user.hashed_password = hash_password(payload.new_password)
    await db.commit()
    return {"message": "Password changed successfully"}


@router.post("/admin/reset-password")
async def admin_reset_password(
    payload: AdminPasswordResetRequest,
    admin: User = Depends(get_current_app_admin),
    db: AsyncSession = Depends(get_db),
):
    import uuid as _uuid
    result = await db.execute(select(User).where(User.id == _uuid.UUID(payload.user_id)))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    target.hashed_password = hash_password(payload.new_password)

    # Notification
    notification = Notification(
        user_id=target.id,
        notification_type=NotificationType.ADMIN_PASSWORD_RESET,
        title="Hasło zostało zmienione",
        body="Twoje hasło zostało zmienione przez administratora.",
    )
    db.add(notification)

    # Audit log
    log = AuditLog(
        actor_id=admin.id,
        target_user_id=target.id,
        action="admin_password_reset",
        resource_type="user",
        resource_id=str(target.id),
    )
    db.add(log)
    await db.commit()
    return {"message": "Password reset successfully"}
