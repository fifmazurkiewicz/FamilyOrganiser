"""Shopping list management service."""
import uuid
from datetime import datetime, timezone
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.exceptions import NotFoundError
from app.models.shopping import ShoppingList, ShoppingItem
from app.schemas.shopping import ShoppingListCreate, ShoppingListUpdate, ShoppingItemCreate, ShoppingItemUpdate


class ShoppingService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Lists ──

    async def create_list(self, user_id: uuid.UUID, data: ShoppingListCreate) -> ShoppingList:
            lst = ShoppingList(
                family_group_id=data.family_group_id,
                name=data.name,
                created_by=user_id,
            )
            self._session.add(lst)
            await self._session.commit()
            # Re-fetch with eager-loaded items to avoid MissingGreenlet on lazy access
            result = await self._session.execute(
                select(ShoppingList)
                .options(selectinload(ShoppingList.items))
                .where(ShoppingList.id == lst.id)
            )
            return result.scalars().first()

    async def list_lists(self, family_group_id: uuid.UUID) -> List[ShoppingList]:
        result = await self._session.execute(
            select(ShoppingList)
            .options(selectinload(ShoppingList.items))
            .where(ShoppingList.family_group_id == family_group_id)
            .order_by(ShoppingList.created_at.desc())
        )
        return list(result.scalars().unique().all())

    async def get_list(self, list_id: uuid.UUID) -> ShoppingList:
        result = await self._session.execute(
            select(ShoppingList).options(selectinload(ShoppingList.items)).where(ShoppingList.id == list_id)
        )
        lst = result.scalars().first()
        if lst is None:
            raise NotFoundError(f"ShoppingList {list_id} not found")
        return lst

    async def update_list(self, list_id: uuid.UUID, data: ShoppingListUpdate) -> ShoppingList:
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

    # ── Items ──

    async def create_item(self, user_id: uuid.UUID, list_id: uuid.UUID, data: ShoppingItemCreate) -> ShoppingItem:
        item = ShoppingItem(
            list_id=list_id,
            name=data.name,
            quantity=data.quantity,
            added_by=user_id,
        )
        self._session.add(item)
        await self._session.commit()
        await self._session.refresh(item)
        return item

    async def list_items(self, list_id: uuid.UUID, include_done: bool = False) -> List[ShoppingItem]:
        stmt = select(ShoppingItem).where(ShoppingItem.list_id == list_id)
        if not include_done:
            stmt = stmt.where(ShoppingItem.is_bought == False)
        stmt = stmt.order_by(ShoppingItem.is_bought.asc(), ShoppingItem.name.asc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_item(self, item_id: uuid.UUID, data: ShoppingItemUpdate) -> ShoppingItem:
        item = await self._session.get(ShoppingItem, item_id)
        if not item:
            raise NotFoundError(f"ShoppingItem {item_id} not found")
        if data.name is not None:
            item.name = data.name
        if data.quantity is not None:
            item.quantity = data.quantity
        if data.is_bought is not None:
            item.is_bought = data.is_bought
        await self._session.commit()
        await self._session.refresh(item)
        return item

    async def toggle_bought(self, user_id: uuid.UUID, item_id: uuid.UUID) -> ShoppingItem:
        item = await self._session.get(ShoppingItem, item_id)
        if not item:
            raise NotFoundError(f"ShoppingItem {item_id} not found")
        item.is_bought = not item.is_bought
        if item.is_bought:
            item.bought_by = user_id
            item.bought_at = datetime.now(timezone.utc)
        else:
            item.bought_by = None
            item.bought_at = None
        await self._session.commit()
        await self._session.refresh(item)
        return item

    async def delete_item(self, item_id: uuid.UUID) -> None:
        item = await self._session.get(ShoppingItem, item_id)
        if not item:
            raise NotFoundError(f"ShoppingItem {item_id} not found")
        await self._session.delete(item)
        await self._session.commit()
