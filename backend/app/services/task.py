import uuid
from datetime import datetime, timezone
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.task import TaskList, TaskItem
from app.models.notification import NotificationType
from app.repositories.task import TaskListRepository, TaskItemRepository
from app.schemas.task import (
    TaskListCreate, TaskListUpdate, TaskListResponse,
    TaskItemCreate, TaskItemUpdate, TaskItemResponse,
)
from app.services.notification import NotificationService


class TaskService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.list_repo = TaskListRepository(db)
        self.item_repo = TaskItemRepository(db)

    # ── lists ──────────────────────────────────────────────

    async def list_lists(self, family_group_id: uuid.UUID) -> List[TaskListResponse]:
        lists = await self.list_repo.list_for_family(family_group_id)
        return [TaskListResponse.model_validate(l) for l in lists]

    async def create_list(
        self, user_id: uuid.UUID, data: TaskListCreate
    ) -> TaskListResponse:
        lst = TaskList(
            family_group_id=data.family_group_id,
            name=data.name,
            created_by=user_id,
        )
        await self.list_repo.add(lst)
        await self.list_repo.commit()
        return TaskListResponse.model_validate(lst)

    async def get_list(self, list_id: uuid.UUID) -> TaskListResponse:
        lst = await self.list_repo.get_or_raise(list_id)
        return TaskListResponse.model_validate(lst)

    async def update_list(
        self, list_id: uuid.UUID, data: TaskListUpdate
    ) -> TaskListResponse:
        lst = await self.list_repo.get_or_raise(list_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(lst, field, value)
        await self.list_repo.commit()
        return TaskListResponse.model_validate(lst)

    async def delete_list(self, list_id: uuid.UUID) -> None:
        lst = await self.list_repo.get_or_raise(list_id)
        await self.list_repo.delete(lst)
        await self.list_repo.commit()

    # ── items ──────────────────────────────────────────────

    async def list_items(self, list_id: uuid.UUID, include_done: bool = False) -> List[TaskItemResponse]:
        items = await self.item_repo.list_for_list(list_id, include_done=include_done)
        return [TaskItemResponse.model_validate(i) for i in items]

    async def create_item(
        self, list_id: uuid.UUID, data: TaskItemCreate
    ) -> TaskItemResponse:
        item = TaskItem(
            list_id=list_id,
            title=data.title,
            assigned_to=data.assigned_to,
            due_date=data.due_date,
        )
        await self.item_repo.add(item)
        await self.item_repo.commit()
        return TaskItemResponse.model_validate(item)

    async def update_item(
        self, item_id: uuid.UUID, data: TaskItemUpdate
    ) -> TaskItemResponse:
        item = await self.item_repo.get_or_raise(item_id)
        for field, value in data.model_dump(exclude_none=True).items():
            if field == "is_done":
                continue  # handled by toggle_done
            setattr(item, field, value)
        await self.item_repo.commit()
        return TaskItemResponse.model_validate(item)

    async def toggle_done(self, user_id: uuid.UUID, item_id: uuid.UUID) -> TaskItemResponse:
        item = await self.item_repo.get_or_raise(item_id)
        item.is_done = not item.is_done
        if item.is_done:
            item.done_by = user_id
            item.done_at = datetime.now(timezone.utc)
        else:
            item.done_by = None
            item.done_at = None
        await self.item_repo.commit()

        # Notify the person who assigned the task when it's completed
        if item.is_done and item.assigned_to and item.assigned_to != user_id:
            notif_svc = NotificationService(self.db)
            await notif_svc.create(
                user_id=item.assigned_to,
                notification_type=NotificationType.TASK_COMPLETED,
                title="Zadanie ukończone",
                body=f"Zadanie \"{item.title}\" zostało ukończone.",
                data={"item_id": str(item.id)},
            )

        return TaskItemResponse.model_validate(item)

    async def delete_item(self, item_id: uuid.UUID) -> None:
        item = await self.item_repo.get_or_raise(item_id)
        await self.item_repo.delete(item)
        await self.item_repo.commit()