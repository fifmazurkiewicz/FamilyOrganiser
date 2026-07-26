import uuid
from datetime import datetime, timezone
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.shopping import ShoppingList, ShoppingItem
from app.models.family import FamilyMembership
from app.models.notification import NotificationType
from app.repositories.shopping import ShoppingListRepository, ShoppingItemRepository
from app.schemas.shopping import (
    ShoppingListCreate, ShoppingListUpdate, ShoppingListResponse,
    ShoppingItemCreate, ShoppingItemUpdate, ShoppingItemResponse,
)
from app.services.notification import NotificationService


class ShoppingService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.list_repo = ShoppingListRepository(db)
        self.item_repo = ShoppingItemRepository(db)

    async def _get_family_members(self, family_group_id: uuid.UUID) -> List[uuid.UUID]:
        """Get all user IDs who are members of the given family group."""
        result = await self.db.execute(
            select(FamilyMembership.user_id).where(
                FamilyMembership.family_group_id == family_group_id
            )
        )
        return [row[0] for row in result.all()]

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
        lst = await self.list_repo.get_or_raise(lst.id)
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

    async def list_items(self, list_id: uuid.UUID, include_done: bool = False) -> List[ShoppingItemResponse]:
        items = await self.item_repo.list_for_list(list_id, include_done=include_done)
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

        # Notify family group members about the new item
        lst = await self.list_repo.get_or_raise(list_id)
        member_ids = await self._get_family_members(lst.family_group_id)
        notif_svc = NotificationService(self.db)
        for member_id in member_ids:
            if member_id != user_id:
                await notif_svc.create(
                    user_id=member_id,
                    notification_type=NotificationType.SHOPPING_ITEM_ADDED,
                    title="Nowy produkt na liście zakupów",
                    body=f"Dodano \"{data.name}\" (x{data.quantity}) do listy \"{lst.name}\".",
                    data={"list_id": str(list_id), "item_id": str(item.id)},
                )

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

        # Notify the person who added the item when it's bought
        if item.is_bought and item.added_by != user_id:
            notif_svc = NotificationService(self.db)
            lst = await self.list_repo.get_or_raise(item.list_id)
            await notif_svc.create(
                user_id=item.added_by,
                notification_type=NotificationType.SHOPPING_ITEM_BOUGHT,
                title="Produkt kupiony!",
                body=f"\"{item.name}\" z listy \"{lst.name}\" został kupiony.",
                data={"list_id": str(item.list_id), "item_id": str(item.id)},
            )

        return ShoppingItemResponse.model_validate(item)

    async def delete_item(self, item_id: uuid.UUID) -> None:
        item = await self.item_repo.get_or_raise(item_id)
        await self.item_repo.delete(item)
        await self.item_repo.commit()