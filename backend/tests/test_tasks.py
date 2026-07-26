"""Unit tests for TaskService — CRUD lists, CRUD items, toggle done."""

import uuid
import pytest
import pytest_asyncio
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.task import TaskService
from app.schemas.task import (
    TaskListCreate,
    TaskListUpdate,
    TaskItemCreate,
    TaskItemUpdate,
)
from app.core.exceptions import NotFoundError


class TestTaskListCRUD:
    async def test_create_list(self, db_session: AsyncSession, test_user, family_group):
        svc = TaskService(db_session)
        data = TaskListCreate(name="Chores", family_group_id=family_group.id)
        result = await svc.create_list(test_user.id, data)

        assert result.id is not None
        assert result.name == "Chores"
        assert result.family_group_id == family_group.id
        assert result.created_by == test_user.id
        assert result.items == []

    async def test_list_lists(self, db_session: AsyncSession, test_user, family_group):
        svc = TaskService(db_session)
        await svc.create_list(
            test_user.id, TaskListCreate(name="Daily", family_group_id=family_group.id)
        )
        await svc.create_list(
            test_user.id, TaskListCreate(name="Weekly", family_group_id=family_group.id)
        )

        lists = await svc.list_lists(family_group.id)
        assert len(lists) == 2
        names = {l.name for l in lists}
        assert names == {"Daily", "Weekly"}

    async def test_get_list(self, db_session: AsyncSession, test_user, family_group):
        svc = TaskService(db_session)
        created = await svc.create_list(
            test_user.id, TaskListCreate(name="Errands", family_group_id=family_group.id)
        )
        fetched = await svc.get_list(created.id)
        assert fetched.name == "Errands"

    async def test_update_list(self, db_session: AsyncSession, test_user, family_group):
        svc = TaskService(db_session)
        created = await svc.create_list(
            test_user.id, TaskListCreate(name="Old", family_group_id=family_group.id)
        )
        updated = await svc.update_list(created.id, TaskListUpdate(name="Renamed"))
        assert updated.name == "Renamed"

    async def test_delete_list(self, db_session: AsyncSession, test_user, family_group):
        svc = TaskService(db_session)
        created = await svc.create_list(
            test_user.id, TaskListCreate(name="Temp", family_group_id=family_group.id)
        )
        await svc.delete_list(created.id)

        with pytest.raises(NotFoundError):
            await svc.get_list(created.id)

    async def test_delete_list_cascades_items(
        self, db_session: AsyncSession, test_user, family_group
    ):
        svc = TaskService(db_session)
        lst = await svc.create_list(
            test_user.id, TaskListCreate(name="Cascade", family_group_id=family_group.id)
        )
        item = await svc.create_item(lst.id, TaskItemCreate(title="Task 1"))
        await svc.delete_list(lst.id)

        # Verify item is also gone by trying to fetch it through a new service
        with pytest.raises(NotFoundError):
            await svc.get_list(lst.id)


class TestTaskItemCRUD:
    @pytest_asyncio.fixture
    async def task_list(self, db_session: AsyncSession, test_user, family_group):
        """Create a list directly to avoid MissingGreenlet on lazy .items."""
        from app.models.task import TaskList
        lst = TaskList(
            family_group_id=family_group.id,
            name="Tasks",
            created_by=test_user.id,
        )
        db_session.add(lst)
        await db_session.flush()
        await db_session.refresh(lst)
        _ = lst.items  # eagerly access
        return lst

    async def test_create_item(
        self, db_session: AsyncSession, test_user, task_list
    ):
        svc = TaskService(db_session)
        due = date(2026, 8, 1)
        item = await svc.create_item(
            task_list.id,
            TaskItemCreate(title="Clean kitchen", assigned_to=test_user.id, due_date=due),
        )

        assert item.id is not None
        assert item.title == "Clean kitchen"
        assert item.assigned_to == test_user.id
        assert item.due_date == due
        assert item.is_done is False
        assert item.list_id == task_list.id

    async def test_list_items(
        self, db_session: AsyncSession, test_user, task_list
    ):
        svc = TaskService(db_session)
        await svc.create_item(task_list.id, TaskItemCreate(title="A"))
        await svc.create_item(task_list.id, TaskItemCreate(title="B"))

        items = await svc.list_items(task_list.id)
        assert len(items) == 2

    async def test_update_item(
        self, db_session: AsyncSession, test_user, task_list
    ):
        svc = TaskService(db_session)
        created = await svc.create_item(task_list.id, TaskItemCreate(title="Old Title"))
        updated = await svc.update_item(
            created.id, TaskItemUpdate(title="New Title")
        )
        assert updated.title == "New Title"

    async def test_toggle_done_on(
        self, db_session: AsyncSession, test_user, task_list
    ):
        svc = TaskService(db_session)
        item = await svc.create_item(task_list.id, TaskItemCreate(title="Mark me done"))
        toggled = await svc.toggle_done(test_user.id, item.id)

        assert toggled.is_done is True
        assert toggled.done_by == test_user.id
        assert toggled.done_at is not None

    async def test_toggle_done_off(
        self, db_session: AsyncSession, test_user, task_list
    ):
        svc = TaskService(db_session)
        item = await svc.create_item(task_list.id, TaskItemCreate(title="Undo me"))
        # Toggle on first
        await svc.toggle_done(test_user.id, item.id)
        # Toggle off
        toggled = await svc.toggle_done(test_user.id, item.id)

        assert toggled.is_done is False
        assert toggled.done_by is None
        assert toggled.done_at is None

    async def test_delete_item(
        self, db_session: AsyncSession, test_user, task_list
    ):
        svc = TaskService(db_session)
        item = await svc.create_item(task_list.id, TaskItemCreate(title="Delete me"))
        await svc.delete_item(item.id)

        items = await svc.list_items(task_list.id)
        assert len(items) == 0