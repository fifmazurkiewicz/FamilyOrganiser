"""Notification service."""
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.notification import Notification, NotificationType
from app.services.family import FamilyService


class NotificationService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list(self, user_id: UUID, *, unread_only: bool = False) -> List[Notification]:
        conditions = [Notification.user_id == user_id]
        if unread_only:
            conditions.append(Notification.is_read == False)

        result = await self._session.execute(
            select(Notification)
            .where(*conditions)
            .order_by(Notification.created_at.desc())
            .limit(100)
        )
        return list(result.scalars().all())

    async def unread_count(self, user_id: UUID) -> int:
        result = await self._session.execute(
            select(func.count()).where(
                Notification.user_id == user_id,
                Notification.is_read == False,
            )
        )
        return result.scalar() or 0

    async def mark_read(self, notification_id: UUID, user_id: UUID) -> Notification:
        notif = await self._session.get(Notification, notification_id)
        if not notif:
            raise NotFoundError("Notification not found")
        if notif.user_id != user_id:
            raise ForbiddenError("Access denied")
        notif.is_read = True
        notif.read_at = datetime.now(timezone.utc)
        await self._session.commit()
        return notif

    async def mark_all_read(self, user_id: UUID) -> int:
        result = await self._session.execute(
            select(Notification).where(
                Notification.user_id == user_id,
                Notification.is_read == False,
            )
        )
        notifications = result.scalars().all()
        now = datetime.now(timezone.utc)
        for notif in notifications:
            notif.is_read = True
            notif.read_at = now
        await self._session.commit()
        return len(notifications)

    async def create(
        self,
        user_id: UUID,
        notification_type: NotificationType,
        title: str,
        body: str,
        data: Optional[dict] = None,
    ) -> Notification:
        notif = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            body=body,
            data=data,
        )
        self._session.add(notif)
        await self._session.flush()
        await self._session.refresh(notif)
        await self._session.commit()
        return notif

    async def notify_group_members_except(
        self,
        family_group_id: UUID,
        actor_id: UUID,
        notification_type: NotificationType,
        title: str,
        body: str,
        *,
        data: Optional[dict] = None,
    ) -> None:
        """Notify all group members except the actor."""
        members = await FamilyService(self._session).list_members(family_group_id)
        for membership in members:
            if membership.user_id == actor_id:
                continue
            await self.create(
                membership.user_id,
                notification_type,
                title,
                body,
                data=data,
            )
