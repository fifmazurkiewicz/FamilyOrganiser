"""Task management service."""
import uuid
from datetime import datetime, timezone
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.exceptions import NotFoundError
from app.models.task import TaskList, TaskItem
from app.schemas.task import TaskListCreate, TaskListUpdate, TaskItemCreate, TaskItemUpdate


class TaskService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_list(self, user_id: uuid.UUID, data: TaskListCreate) -> TaskList:
        lst = TaskList(
            family_group_id=data.family_group_id,
            name=data.name,
            created_by=user_id,
        )
        self._session.add(lst)
        await self._session.commit()
        await self._session.refresh(lst)
        return lst

    async def list_lists(self, family_group_id: uuid.UUID) -> List[TaskList]:
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

    async def update_list(self, list_id: uuid.UUID, data: TaskListUpdate) -> TaskList:
        lst = await self.get_list(list_id)
        if data.name is not None:
            lst.name = data.name
        await self._session.commit()
        await self._session.refresh(lst)
        return lst

    async def delete_list(self, list_id: uuid.UUID) -> None:
        lst = await self.get_list(list_id)
        await self._session.delete(lst)
        await self._session.commit()

    async def create_item(self, list_id: uuid.UUID, data: TaskItemCreate) -> TaskItem:
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

    async def list_items(self, list_id: uuid.UUID, include_done: bool = False) -> List[TaskItem]:
        stmt = select(TaskItem).where(TaskItem.list_id == list_id)
        if not include_done:
            stmt = stmt.where(TaskItem.is_done == False)
        stmt = stmt.order_by(TaskItem.is_done.asc(), TaskItem.due_date.asc().nulls_last(), TaskItem.title.asc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_item(self, item_id: uuid.UUID, data: TaskItemUpdate) -> TaskItem:
        item = await self._session.get(TaskItem, item_id)
        if not item:
            raise NotFoundError(f"TaskItem {item_id} not found")
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
        item.is_done = not item.is_done
        if item.is_done:
            item.done_by = user_id
            item.done_at = datetime.now(timezone.utc)
        else:
            item.done_by = None
            item.done_at = None
        await self._session.commit()
        await self._session.refresh(item)
        return item

    async def delete_item(self, item_id: uuid.UUID) -> None:
        item = await self._session.get(TaskItem, item_id)
        if not item:
            raise NotFoundError(f"TaskItem {item_id} not found")
        await self._session.delete(item)
        await self._session.commit()
