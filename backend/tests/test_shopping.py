"""Unit tests for ShoppingService — CRUD lists, CRUD items, toggle bought."""

import uuid
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.shopping import ShoppingService
from app.schemas.shopping import (
    ShoppingListCreate,
    ShoppingListUpdate,
    ShoppingItemCreate,
    ShoppingItemUpdate,
)
from app.core.exceptions import NotFoundError


# ── Lists ──────────────────────────────────────────────────────

class TestShoppingListCRUD:
    async def test_create_list(self, db_session: AsyncSession, test_user, family_group):
        svc = ShoppingService(db_session)
        data = ShoppingListCreate(name="Groceries", family_group_id=family_group.id)
        result = await svc.create_list(test_user.id, data)

        assert result.id is not None
        assert result.name == "Groceries"
        assert result.family_group_id == family_group.id
        assert result.created_by == test_user.id
        assert result.items == []

    async def test_list_lists(self, db_session: AsyncSession, test_user, family_group):
        svc = ShoppingService(db_session)
        # Create two lists
        await svc.create_list(
            test_user.id, ShoppingListCreate(name="List A", family_group_id=family_group.id)
        )
        await svc.create_list(
            test_user.id, ShoppingListCreate(name="List B", family_group_id=family_group.id)
        )

        lists = await svc.list_lists(family_group.id)
        assert len(lists) == 2
        names = {l.name for l in lists}
        assert names == {"List A", "List B"}

    async def test_list_lists_family_isolation(
        self, db_session: AsyncSession, test_user, family_group, family_group2
    ):
        svc = ShoppingService(db_session)
        await svc.create_list(
            test_user.id, ShoppingListCreate(name="Family 1 List", family_group_id=family_group.id)
        )
        await svc.create_list(
            test_user.id, ShoppingListCreate(name="Family 2 List", family_group_id=family_group2.id)
        )

        f1_lists = await svc.list_lists(family_group.id)
        f2_lists = await svc.list_lists(family_group2.id)

        assert len(f1_lists) == 1
        assert f1_lists[0].name == "Family 1 List"
        assert len(f2_lists) == 1
        assert f2_lists[0].name == "Family 2 List"

    async def test_get_list(self, db_session: AsyncSession, test_user, family_group):
        svc = ShoppingService(db_session)
        created = await svc.create_list(
            test_user.id, ShoppingListCreate(name="To Buy", family_group_id=family_group.id)
        )
        fetched = await svc.get_list(created.id)
        assert fetched.id == created.id
        assert fetched.name == "To Buy"

    async def test_get_list_not_found(self, db_session: AsyncSession, test_user, family_group):
        svc = ShoppingService(db_session)
        with pytest.raises(NotFoundError):
            await svc.get_list(uuid.uuid4())

    async def test_update_list(self, db_session: AsyncSession, test_user, family_group):
        svc = ShoppingService(db_session)
        created = await svc.create_list(
            test_user.id, ShoppingListCreate(name="Old Name", family_group_id=family_group.id)
        )
        updated = await svc.update_list(created.id, ShoppingListUpdate(name="New Name"))
        assert updated.name == "New Name"

        # Verify persistence
        fetched = await svc.get_list(created.id)
        assert fetched.name == "New Name"

    async def test_delete_list(self, db_session: AsyncSession, test_user, family_group):
        svc = ShoppingService(db_session)
        created = await svc.create_list(
            test_user.id, ShoppingListCreate(name="Temp", family_group_id=family_group.id)
        )
        await svc.delete_list(created.id)

        with pytest.raises(NotFoundError):
            await svc.get_list(created.id)

    async def test_delete_list_with_items(
        self, db_session: AsyncSession, test_user, family_group
    ):
        """Deleting a list should cascade-delete its items."""
        svc = ShoppingService(db_session)
        lst = await svc.create_list(
            test_user.id, ShoppingListCreate(name="With Items", family_group_id=family_group.id)
        )
        await svc.create_item(test_user.id, lst.id, ShoppingItemCreate(name="Milk"))
        await svc.create_item(test_user.id, lst.id, ShoppingItemCreate(name="Bread"))

        await svc.delete_list(lst.id)

        with pytest.raises(NotFoundError):
            await svc.get_list(lst.id)


# ── Items ──────────────────────────────────────────────────────

class TestShoppingItemCRUD:
    @pytest_asyncio.fixture
    async def shopping_list(self, db_session: AsyncSession, test_user, family_group):
        """Create a list directly to avoid MissingGreenlet on lazy .items."""
        from app.models.shopping import ShoppingList
        lst = ShoppingList(
            family_group_id=family_group.id,
            name="Test List",
            created_by=test_user.id,
        )
        db_session.add(lst)
        await db_session.flush()
        await db_session.refresh(lst)
        _ = lst.items  # eagerly access to avoid lazy-load in model_validate
        return lst

    async def test_create_item(
        self, db_session: AsyncSession, test_user, shopping_list
    ):
        svc = ShoppingService(db_session)
        item = await svc.create_item(
            test_user.id, shopping_list.id, ShoppingItemCreate(name="Eggs", quantity=12)
        )

        assert item.id is not None
        assert item.name == "Eggs"
        assert item.quantity == 12
        assert item.added_by == test_user.id
        assert item.is_bought is False
        assert item.list_id == shopping_list.id

    async def test_create_item_default_quantity(
        self, db_session: AsyncSession, test_user, shopping_list
    ):
        svc = ShoppingService(db_session)
        item = await svc.create_item(
            test_user.id, shopping_list.id, ShoppingItemCreate(name="Milk")
        )
        assert item.quantity == 1

    async def test_list_items(
        self, db_session: AsyncSession, test_user, shopping_list
    ):
        svc = ShoppingService(db_session)
        await svc.create_item(test_user.id, shopping_list.id, ShoppingItemCreate(name="A"))
        await svc.create_item(test_user.id, shopping_list.id, ShoppingItemCreate(name="B"))
        await svc.create_item(test_user.id, shopping_list.id, ShoppingItemCreate(name="C"))

        items = await svc.list_items(shopping_list.id)
        assert len(items) == 3

    async def test_update_item(
        self, db_session: AsyncSession, test_user, shopping_list
    ):
        svc = ShoppingService(db_session)
        created = await svc.create_item(
            test_user.id, shopping_list.id, ShoppingItemCreate(name="Old", quantity=1)
        )
        updated = await svc.update_item(
            created.id, ShoppingItemUpdate(name="New", quantity=5)
        )
        assert updated.name == "New"
        assert updated.quantity == 5

    async def test_toggle_bought_on(
        self, db_session: AsyncSession, test_user, shopping_list
    ):
        svc = ShoppingService(db_session)
        item = await svc.create_item(
            test_user.id, shopping_list.id, ShoppingItemCreate(name="Apples")
        )
        toggled = await svc.toggle_bought(test_user.id, item.id)

        assert toggled.is_bought is True
        assert toggled.bought_by == test_user.id
        assert toggled.bought_at is not None

    async def test_toggle_bought_off(
        self, db_session: AsyncSession, test_user, shopping_list
    ):
        svc = ShoppingService(db_session)
        item = await svc.create_item(
            test_user.id, shopping_list.id, ShoppingItemCreate(name="Bananas")
        )
        # First toggle on
        await svc.toggle_bought(test_user.id, item.id)
        # Now toggle off
        toggled = await svc.toggle_bought(test_user.id, item.id)

        assert toggled.is_bought is False
        assert toggled.bought_by is None
        assert toggled.bought_at is None

    async def test_delete_item(
        self, db_session: AsyncSession, test_user, shopping_list
    ):
        svc = ShoppingService(db_session)
        item = await svc.create_item(
            test_user.id, shopping_list.id, ShoppingItemCreate(name="Delete me")
        )
        await svc.delete_item(item.id)

        items = await svc.list_items(shopping_list.id)
        assert len(items) == 0