from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_app_admin
from app.db.base import get_db
from app.models.user import User
from app.schemas.auth import (
    AdminPasswordResetRequest,
    LoginRequest,
    PasswordChangeRequest,
    RefreshRequest,
    RegisterRequest,
    SecurityQuestionResponse,
    SecurityQuestionResetRequest,
    TokenResponse,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    access, refresh = await svc.register(
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
        default_currency=payload.default_currency,
        security_question=payload.security_question,
        security_answer=payload.security_answer,
    )
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    access, refresh = await svc.login(payload.email, payload.password)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    access, new_refresh = await svc.refresh(payload.refresh_token)
    return TokenResponse(access_token=access, refresh_token=new_refresh)


@router.get("/security-question", response_model=SecurityQuestionResponse)
async def get_security_question(email: str, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    question = await svc.get_security_question(email)
    return SecurityQuestionResponse(question=question)


@router.post("/reset-password/security-question")
async def reset_via_security_question(
    payload: SecurityQuestionResetRequest, db: AsyncSession = Depends(get_db)
):
    svc = AuthService(db)
    await svc.reset_password_via_security_question(
        payload.email, payload.answer, payload.new_password
    )
    return {"message": "Password reset successfully"}


@router.post("/change-password")
async def change_password(
    payload: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = AuthService(db)
    await svc.change_password(current_user, payload.current_password, payload.new_password)
    return {"message": "Password changed successfully"}


@router.post("/admin/reset-password")
async def admin_reset_password(
    payload: AdminPasswordResetRequest,
    admin: User = Depends(get_current_app_admin),
    db: AsyncSession = Depends(get_db),
):
    svc = AuthService(db)
    await svc.admin_reset_password(admin, payload.user_id, payload.new_password)
    return {"message": "Password reset successfully"}
