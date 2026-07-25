import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.services.shopping import ShoppingService
from app.schemas.shopping import (
    ShoppingListCreate, ShoppingListUpdate, ShoppingListResponse,
    ShoppingItemCreate, ShoppingItemUpdate, ShoppingItemResponse,
)

router = APIRouter(prefix="/shopping", tags=["Shopping"])

# ── lists ──────────────────────────────────────────────────

@router.get("/lists", response_model=list[ShoppingListResponse])
async def list_lists(
    family_group_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ShoppingService(db).list_lists(family_group_id)


@router.post("/lists", response_model=ShoppingListResponse, status_code=201)
async def create_list(
    data: ShoppingListCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ShoppingService(db).create_list(current_user.id, data)


@router.get("/lists/{list_id}", response_model=ShoppingListResponse)
async def get_list(
    list_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ShoppingService(db).get_list(list_id)


@router.patch("/lists/{list_id}", response_model=ShoppingListResponse)
async def update_list(
    list_id: uuid.UUID,
    data: ShoppingListUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ShoppingService(db).update_list(list_id, data)


@router.delete("/lists/{list_id}", status_code=204)
async def delete_list(
    list_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ShoppingService(db).delete_list(list_id)

# ── items ──────────────────────────────────────────────────

@router.get("/lists/{list_id}/items", response_model=list[ShoppingItemResponse])
async def list_items(
    list_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ShoppingService(db).list_items(list_id)


@router.post("/lists/{list_id}/items", response_model=ShoppingItemResponse, status_code=201)
async def create_item(
    list_id: uuid.UUID,
    data: ShoppingItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ShoppingService(db).create_item(current_user.id, list_id, data)


@router.patch("/items/{item_id}", response_model=ShoppingItemResponse)
async def update_item(
    item_id: uuid.UUID,
    data: ShoppingItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ShoppingService(db).update_item(item_id, data)


@router.post("/items/{item_id}/toggle", response_model=ShoppingItemResponse)
async def toggle_bought(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ShoppingService(db).toggle_bought(current_user.id, item_id)


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ShoppingService(db).delete_item(item_id)