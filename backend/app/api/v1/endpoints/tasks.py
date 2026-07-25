import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.services.task import TaskService
from app.schemas.task import (
    TaskListCreate, TaskListUpdate, TaskListResponse,
    TaskItemCreate, TaskItemUpdate, TaskItemResponse,
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# ── lists ──────────────────────────────────────────────────

@router.get("/lists", response_model=list[TaskListResponse])
async def list_lists(
    family_group_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await TaskService(db).list_lists(family_group_id)


@router.post("/lists", response_model=TaskListResponse, status_code=201)
async def create_list(
    data: TaskListCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await TaskService(db).create_list(current_user.id, data)


@router.get("/lists/{list_id}", response_model=TaskListResponse)
async def get_list(
    list_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await TaskService(db).get_list(list_id)


@router.patch("/lists/{list_id}", response_model=TaskListResponse)
async def update_list(
    list_id: uuid.UUID,
    data: TaskListUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await TaskService(db).update_list(list_id, data)


@router.delete("/lists/{list_id}", status_code=204)
async def delete_list(
    list_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await TaskService(db).delete_list(list_id)

# ── items ──────────────────────────────────────────────────

@router.get("/lists/{list_id}/items", response_model=list[TaskItemResponse])
async def list_items(
    list_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await TaskService(db).list_items(list_id)


@router.post("/lists/{list_id}/items", response_model=TaskItemResponse, status_code=201)
async def create_item(
    list_id: uuid.UUID,
    data: TaskItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await TaskService(db).create_item(list_id, data)


@router.patch("/items/{item_id}", response_model=TaskItemResponse)
async def update_item(
    item_id: uuid.UUID,
    data: TaskItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await TaskService(db).update_item(item_id, data)


@router.post("/items/{item_id}/toggle", response_model=TaskItemResponse)
async def toggle_done(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await TaskService(db).toggle_done(current_user.id, item_id)


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await TaskService(db).delete_item(item_id)