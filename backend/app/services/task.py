"""Task management service."""
import uuid
from datetime import datetime, timezone
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.models.notification import NotificationType
from app.models.task import TaskItem, TaskList
from app.models.user import User
from app.schemas.task import TaskItemCreate, TaskItemUpdate, TaskListCreate, TaskListUpdate
from app.services.group_access import require_family_member
from app.services.notification import NotificationService


class TaskService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _ensure_list_access(self, user_id: uuid.UUID, list_id: uuid.UUID) -> TaskList:
        lst = await self.get_list(list_id)
        await require_family_member(self._session, user_id, lst.family_group_id)
        return lst

    async def create_list(self, user_id: uuid.UUID, data: TaskListCreate) -> TaskList:
        await require_family_member(self._session, user_id, data.family_group_id)
        lst = TaskList(
            family_group_id=data.family_group_id,
            name=data.name,
            created_by=user_id,
        )
        self._session.add(lst)
        await self._session.commit()
        result = await self._session.execute(
            select(TaskList)
            .options(selectinload(TaskList.items))
            .where(TaskList.id == lst.id)
        )
        return result.scalars().first()

    async def list_lists(self, user_id: uuid.UUID, family_group_id: uuid.UUID) -> List[TaskList]:
        await require_family_member(self._session, user_id, family_group_id)
        result = await self._session.execute(
            select(TaskList)
            .options(selectinload(TaskList.items))
            .where(TaskList.family_group_id == family_group_id)
            .order_by(TaskList.created_at.desc())
        )
        return list(result.scalars().unique().all())

    async def get_list(self, list_id: uuid.UUID) -> TaskList:
        result = await self._session.execute(
            select(TaskList).options(selectinload(TaskList.items)).where(TaskList.id == list_id)
        )
        lst = result.scalars().first()
        if lst is None:
            raise NotFoundError(f"TaskList {list_id} not found")
        return lst

    async def update_list(
        self, user_id: uuid.UUID, list_id: uuid.UUID, data: TaskListUpdate
    ) -> TaskList:
        lst = await self._ensure_list_access(user_id, list_id)
        if data.name is not None:
            lst.name = data.name
        await self._session.commit()
        await self._session.refresh(lst)
        return lst

    async def delete_list(self, user_id: uuid.UUID, list_id: uuid.UUID) -> None:
        lst = await self._ensure_list_access(user_id, list_id)
        await self._session.delete(lst)
        await self._session.commit()

    async def create_item(
        self, user_id: uuid.UUID, list_id: uuid.UUID, data: TaskItemCreate
    ) -> TaskItem:
        lst = await self._ensure_list_access(user_id, list_id)
        item = TaskItem(
            list_id=list_id,
            title=data.title,
            assigned_to=data.assigned_to,
            due_date=data.due_date,
        )
        self._session.add(item)
        await self._session.commit()
        await self._session.refresh(item)
        return item

    async def list_items(
        self, user_id: uuid.UUID, list_id: uuid.UUID, include_done: bool = False
    ) -> List[TaskItem]:
        await self._ensure_list_access(user_id, list_id)
        stmt = select(TaskItem).where(TaskItem.list_id == list_id)
        if not include_done:
            stmt = stmt.where(TaskItem.is_done == False)
        stmt = stmt.order_by(
            TaskItem.is_done.asc(), TaskItem.due_date.asc().nulls_last(), TaskItem.title.asc()
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_item(
        self, user_id: uuid.UUID, item_id: uuid.UUID, data: TaskItemUpdate
    ) -> TaskItem:
        item = await self._session.get(TaskItem, item_id)
        if not item:
            raise NotFoundError(f"TaskItem {item_id} not found")
        await self._ensure_list_access(user_id, item.list_id)
        if data.title is not None:
            item.title = data.title
        if data.assigned_to is not None:
            item.assigned_to = data.assigned_to
        if data.is_done is not None:
            item.is_done = data.is_done
        if data.due_date is not None:
            item.due_date = data.due_date
        await self._session.commit()
        await self._session.refresh(item)
        return item

    async def toggle_done(self, user_id: uuid.UUID, item_id: uuid.UUID) -> TaskItem:
        item = await self._session.get(TaskItem, item_id)
        if not item:
            raise NotFoundError(f"TaskItem {item_id} not found")
        lst = await self._ensure_list_access(user_id, item.list_id)
        was_done = item.is_done
        item.is_done = not item.is_done
        if item.is_done:
            item.done_by = user_id
            item.done_at = datetime.now(timezone.utc)
        else:
            item.done_by = None
            item.done_at = None
        await self._session.commit()
        await self._session.refresh(item)

        if item.is_done and not was_done:
            actor = await self._session.get(User, user_id)
            actor_name = actor.full_name if actor else "Ktoś"
            await NotificationService(self._session).notify_group_members_except(
                lst.family_group_id,
                user_id,
                NotificationType.TASK_COMPLETED,
                "Zadania",
                f"{actor_name} ukończył(a) zadanie „{item.title}” na liście „{lst.name}”.",
            )
        return item

    async def delete_item(self, user_id: uuid.UUID, item_id: uuid.UUID) -> None:
        item = await self._session.get(TaskItem, item_id)
        if not item:
            raise NotFoundError(f"TaskItem {item_id} not found")
        await self._ensure_list_access(user_id, item.list_id)
        await self._session.delete(item)
        await self._session.commit()
