"""Notification service."""
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.notification import Notification
from app.repositories.notification import NotificationRepository


class NotificationService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = NotificationRepository(session)

    async def list(self, user_id: UUID, *, unread_only: bool = False) -> list[Notification]:
        return await self._repo.list_for_user(user_id, unread_only=unread_only)

    async def unread_count(self, user_id: UUID) -> int:
        return await self._repo.unread_count(user_id)

    async def mark_read(self, notification_id: UUID, user_id: UUID) -> Notification:
        notif = await self._repo.get(notification_id)
        if not notif:
            raise NotFoundError("Notification not found")
        if notif.user_id != user_id:
            raise ForbiddenError("Access denied")
        notif.is_read = True
        notif.read_at = datetime.now(timezone.utc)
        await self._session.commit()
        return notif

    async def mark_all_read(self, user_id: UUID) -> int:
        notifications = await self._repo.list_unread_for_user(user_id)
        now = datetime.now(timezone.utc)
        for notif in notifications:
            notif.is_read = True
            notif.read_at = now
        await self._session.commit()
        return len(notifications)
