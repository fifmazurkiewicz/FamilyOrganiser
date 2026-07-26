import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.shopping import ShoppingList, ShoppingItem
from app.repositories.base import BaseRepository


class ShoppingListRepository(BaseRepository[ShoppingList]):
    model = ShoppingList

    async def list_for_family(self, family_group_id: uuid.UUID) -> List[ShoppingList]:
        result = await self._session.execute(
            select(ShoppingList)
            .options(selectinload(ShoppingList.items))
            .where(ShoppingList.family_group_id == family_group_id)
            .order_by(ShoppingList.created_at.desc())
        )
        return list(result.scalars().unique().all())


    async def get_or_raise(self, id):
        result = await self._session.execute(
            select(ShoppingList).options(selectinload(ShoppingList.items)).where(ShoppingList.id == id)
        )
        lst = result.scalars().first()
        if lst is None:
            from app.core.exceptions import NotFoundError
            raise NotFoundError(f"ShoppingList {id} not found")
        return lst


class ShoppingItemRepository(BaseRepository[ShoppingItem]):
    model = ShoppingItem

    async def list_for_list(self, list_id: uuid.UUID, include_done: bool = False) -> List[ShoppingItem]:
        stmt = select(ShoppingItem).where(ShoppingItem.list_id == list_id)
        if not include_done:
            stmt = stmt.where(ShoppingItem.is_bought == False)
        stmt = stmt.order_by(ShoppingItem.is_bought.asc(), ShoppingItem.name.asc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())