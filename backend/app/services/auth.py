"""Authentication and password-management service."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    AccountLockedError,
    BusinessLogicError,
    ConflictError,
    NotFoundError,
    UnauthorizedError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_security_answer,
    verify_password,
    verify_security_answer,
)
from app.models.notification import Notification, NotificationType
from app.models.user import SecurityQuestion, User


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # --- inline UserRepository ---

    async def _get_user_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def _get_security_question(self, user_id) -> SecurityQuestion | None:
        result = await self._session.execute(
            select(SecurityQuestion).where(SecurityQuestion.user_id == user_id)
        )
        return result.scalar_one_or_none()

    # --- auth methods ---

    async def register(
        self,
        email: str,
        password: str,
        full_name: str,
        default_currency: str,
        security_question: str,
        security_answer: str,
    ) -> tuple[str, str]:
        """Create a new user and return (access_token, refresh_token)."""
        if await self._get_user_by_email(email):
            raise ConflictError("Email already registered")

        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            default_currency=default_currency,
        )
        self._session.add(user)
        await self._session.flush()

        sq = SecurityQuestion(
            user_id=user.id,
            question=security_question,
            hashed_answer=hash_security_answer(security_answer),
        )
        self._session.add(sq)
        await self._session.commit()
        await self._session.refresh(user)

        return self._issue_tokens(user)

    async def login(self, email: str, password: str) -> tuple[str, str]:
        user = await self._get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")
        if user.is_locked:
            raise AccountLockedError()
        if not user.is_active:
            raise BusinessLogicError("Account is inactive")
        return self._issue_tokens(user)

    async def refresh(self, refresh_token: str) -> tuple[str, str]:
        import uuid

        data = decode_token(refresh_token)
        if not data or data.get("type") != "refresh":
            raise UnauthorizedError("Invalid refresh token")

        user = await self._session.get(User, uuid.UUID(data["sub"]))
        if not user or not user.is_active or user.is_locked:
            raise UnauthorizedError("User unavailable")
        return self._issue_tokens(user)

    async def get_security_question(self, email: str) -> str:
        user = await self._get_user_by_email(email)
        if not user:
            raise NotFoundError("User not found")
        sq = await self._get_security_question(user.id)
        if not sq:
            raise NotFoundError("No security question configured")
        return sq.question

    async def reset_password_via_security_question(
        self, email: str, answer: str, new_password: str
    ) -> None:
        user = await self._get_user_by_email(email)
        if not user:
            raise NotFoundError("User not found")
        if user.is_locked:
            raise AccountLockedError()

        sq = await self._get_security_question(user.id)
        if not sq:
            raise BusinessLogicError("No security question configured")

        if not verify_security_answer(answer, sq.hashed_answer):
            user.security_question_attempts += 1
            if user.security_question_attempts >= settings.MAX_SECURITY_QUESTION_ATTEMPTS:
                user.is_locked = True
                await self._session.commit()
                raise AccountLockedError()
            await self._session.commit()
            raise BusinessLogicError("Incorrect answer to security question")

        user.hashed_password = hash_password(new_password)
        user.security_question_attempts = 0
        await self._session.commit()

    async def change_password(
        self, user: User, current_password: str, new_password: str
    ) -> None:
        if not verify_password(current_password, user.hashed_password):
            raise BusinessLogicError("Incorrect current password")
        user.hashed_password = hash_password(new_password)
        await self._session.commit()

    async def admin_reset_password(
        self, actor: User, target_user_id: str, new_password: str
    ) -> None:
        import uuid
        from app.models.audit_log import AuditLog

        target = await self._session.get(User, uuid.UUID(target_user_id))
        if not target:
            raise NotFoundError("User not found")

        target.hashed_password = hash_password(new_password)

        notif = Notification(
            user_id=target.id,
            notification_type=NotificationType.ADMIN_PASSWORD_RESET,
            title="Hasło zostało zmienione",
            body="Twoje hasło zostało zmienione przez administratora aplikacji.",
        )
        log = AuditLog(
            actor_id=actor.id,
            target_user_id=target.id,
            action="admin_password_reset",
            resource_type="user",
            resource_id=str(target.id),
        )
        self._session.add(notif)
        self._session.add(log)
        await self._session.commit()

    @staticmethod
    def _issue_tokens(user: User) -> tuple[str, str]:
        sub = str(user.id)
        return (
            create_access_token({"sub": sub}),
            create_refresh_token({"sub": sub}),
        )
