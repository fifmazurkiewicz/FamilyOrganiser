import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.task import TaskList, TaskItem
from app.repositories.base import BaseRepository


class TaskListRepository(BaseRepository[TaskList]):
    model = TaskList

    async def list_for_family(self, family_group_id: uuid.UUID) -> List[TaskList]:
        result = await self._session.execute(
            select(TaskList)
            .options(selectinload(TaskList.items))
            .where(TaskList.family_group_id == family_group_id)
            .order_by(TaskList.created_at.desc())
        )
        return list(result.scalars().unique().all())


    async def get_or_raise(self, id):
        from sqlalchemy.orm import selectinload
        result = await self._session.execute(
            select(TaskList).options(selectinload(TaskList.items)).where(TaskList.id == id)
        )
        lst = result.scalars().first()
        if lst is None:
            from app.core.exceptions import NotFoundError
            raise NotFoundError(f"TaskList {id} not found")
        return lst


class TaskItemRepository(BaseRepository[TaskItem]):
    model = TaskItem

    async def list_for_list(self, list_id: uuid.UUID, include_done: bool = False) -> List[TaskItem]:
        stmt = select(TaskItem).where(TaskItem.list_id == list_id)
        if not include_done:
            stmt = stmt.where(TaskItem.is_done == False)
        stmt = stmt.order_by(TaskItem.is_done.asc(), TaskItem.due_date.asc().nulls_last(), TaskItem.title.asc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())