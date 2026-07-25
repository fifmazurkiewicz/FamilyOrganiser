import uuid
from datetime import datetime, timezone
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.shopping import ShoppingList, ShoppingItem
from app.repositories.shopping import ShoppingListRepository, ShoppingItemRepository
from app.schemas.shopping import (
    ShoppingListCreate, ShoppingListUpdate, ShoppingListResponse,
    ShoppingItemCreate, ShoppingItemUpdate, ShoppingItemResponse,
)


class ShoppingService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.list_repo = ShoppingListRepository(db)
        self.item_repo = ShoppingItemRepository(db)

    # ── lists ──────────────────────────────────────────────

    async def list_lists(self, family_group_id: uuid.UUID) -> List[ShoppingListResponse]:
        lists = await self.list_repo.list_for_family(family_group_id)
        return [ShoppingListResponse.model_validate(l) for l in lists]

    async def create_list(
        self, user_id: uuid.UUID, data: ShoppingListCreate
    ) -> ShoppingListResponse:
        lst = ShoppingList(
            family_group_id=data.family_group_id,
            name=data.name,
            created_by=user_id,
        )
        await self.list_repo.add(lst)
        await self.list_repo.commit()
        return ShoppingListResponse.model_validate(lst)

    async def get_list(self, list_id: uuid.UUID) -> ShoppingListResponse:
        lst = await self.list_repo.get_or_raise(list_id)
        return ShoppingListResponse.model_validate(lst)

    async def update_list(
        self, list_id: uuid.UUID, data: ShoppingListUpdate
    ) -> ShoppingListResponse:
        lst = await self.list_repo.get_or_raise(list_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(lst, field, value)
        await self.list_repo.commit()
        return ShoppingListResponse.model_validate(lst)

    async def delete_list(self, list_id: uuid.UUID) -> None:
        lst = await self.list_repo.get_or_raise(list_id)
        await self.list_repo.delete(lst)
        await self.list_repo.commit()

    # ── items ──────────────────────────────────────────────

    async def list_items(self, list_id: uuid.UUID) -> List[ShoppingItemResponse]:
        items = await self.item_repo.list_for_list(list_id)
        return [ShoppingItemResponse.model_validate(i) for i in items]

    async def create_item(
        self, user_id: uuid.UUID, list_id: uuid.UUID, data: ShoppingItemCreate
    ) -> ShoppingItemResponse:
        item = ShoppingItem(
            list_id=list_id,
            name=data.name,
            quantity=data.quantity,
            added_by=user_id,
        )
        await self.item_repo.add(item)
        await self.item_repo.commit()
        return ShoppingItemResponse.model_validate(item)

    async def update_item(
        self, item_id: uuid.UUID, data: ShoppingItemUpdate
    ) -> ShoppingItemResponse:
        item = await self.item_repo.get_or_raise(item_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(item, field, value)
        await self.item_repo.commit()
        return ShoppingItemResponse.model_validate(item)

    async def toggle_bought(self, user_id: uuid.UUID, item_id: uuid.UUID) -> ShoppingItemResponse:
        item = await self.item_repo.get_or_raise(item_id)
        item.is_bought = not item.is_bought
        if item.is_bought:
            item.bought_by = user_id
            item.bought_at = datetime.now(timezone.utc)
        else:
            item.bought_by = None
            item.bought_at = None
        await self.item_repo.commit()
        return ShoppingItemResponse.model_validate(item)

    async def delete_item(self, item_id: uuid.UUID) -> None:
        item = await self.item_repo.get_or_raise(item_id)
        await self.item_repo.delete(item)
        await self.item_repo.commit()