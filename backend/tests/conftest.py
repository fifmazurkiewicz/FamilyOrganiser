"""Test configuration, fixtures, and helpers for FamilyOrganiser backend tests."""

import asyncio
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler

from app.db.base import Base, get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.family import FamilyGroup, FamilyMembership, FamilyRole
from app.core.config import settings
from app.core.security import create_access_token
import app.models  # noqa: F401 — register all ORM tables for create_all

# ---------------------------------------------------------------------------
# SQLite JSON support — compile JSON as TEXT
# ---------------------------------------------------------------------------

SQLiteTypeCompiler.visit_JSON = lambda self, type_, **kw: "TEXT"

# ---------------------------------------------------------------------------
# Test database
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite+aiosqlite://"


@pytest.fixture(scope="session")
def event_loop_policy():
    """Use the Windows-compatible event loop policy."""
    return asyncio.WindowsSelectorEventLoopPolicy() if hasattr(asyncio, "WindowsSelectorEventLoopPolicy") else asyncio.DefaultEventLoopPolicy()


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Session-scoped async engine — creates/drops all tables once."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    """Per-test async session — connection-level transaction rolls back after each test."""
    async with engine.connect() as conn:
        async with conn.begin() as trans:
            session_factory = async_sessionmaker(
                bind=conn, class_=AsyncSession, expire_on_commit=False
            )
            async with session_factory() as session:
                yield session
            await trans.rollback()


# ---------------------------------------------------------------------------
# Model factories (in-DB)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create and return a test user (already persisted)."""
    user = User(
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User",
        is_approved=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user2(db_session: AsyncSession) -> User:
    """A second test user."""
    user = User(
        email="test2@example.com",
        hashed_password="hashed",
        full_name="Test User 2",
        is_approved=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def family_group(db_session: AsyncSession, test_user: User) -> FamilyGroup:
    """Create and return a test family group with test_user as admin member."""
    group = FamilyGroup(name="Test Family")
    db_session.add(group)
    await db_session.flush()
    db_session.add(
        FamilyMembership(
            user_id=test_user.id,
            family_group_id=group.id,
            role=FamilyRole.ADMIN,
        )
    )
    await db_session.flush()
    await db_session.refresh(group)
    return group


@pytest_asyncio.fixture
async def family_group2(db_session: AsyncSession, test_user2: User) -> FamilyGroup:
    """A second family group (for isolation tests) with test_user2 as admin."""
    group = FamilyGroup(name="Second Family")
    db_session.add(group)
    await db_session.flush()
    db_session.add(
        FamilyMembership(
            user_id=test_user2.id,
            family_group_id=group.id,
            role=FamilyRole.ADMIN,
        )
    )
    await db_session.flush()
    await db_session.refresh(group)
    return group


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """An admin user."""
    user = User(
        email="admin@example.com",
        hashed_password="hashed",
        full_name="Admin User",
        is_app_admin=True,
        is_approved=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


# ---------------------------------------------------------------------------
# Auth token helpers
# ---------------------------------------------------------------------------

def make_auth_token(user: User) -> str:
    """Return a valid Bearer token for the given user."""
    return create_access_token({"sub": str(user.id)})


# ---------------------------------------------------------------------------
# App / client fixtures (for API integration tests)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def app_with_overrides(
    db_session: AsyncSession,
    test_user: User,
):
    """Return the FastAPI app with get_db and get_current_user overridden."""
    from app.main import app

    async def override_get_db():
        try:
            yield db_session
        finally:
            pass

    async def override_get_current_user():
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    yield app

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app_with_overrides) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client pointing at the test app."""
    transport = ASGITransport(app=app_with_overrides)
    base_url = "http://testserver/api/v1"
    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        yield ac


@pytest_asyncio.fixture
async def client_auth_headers(test_user: User) -> dict:
    """Convenience: Authorization header dict."""
    return {"Authorization": f"Bearer {make_auth_token(test_user)}"}


# ---------------------------------------------------------------------------
# Service-level fixture (direct DB session, no HTTP)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def service_db(db_session: AsyncSession):
    """Returns the async DB session for direct service tests."""
    return db_session


# ---------------------------------------------------------------------------
# Model fixtures for new modules (shopping, tasks, budget, investments)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def shopping_list(db_session: AsyncSession, family_group, test_user):
    from app.models.shopping import ShoppingList
    lst = ShoppingList(name="Test List", family_group_id=family_group.id, created_by=test_user.id)
    db_session.add(lst)
    await db_session.flush()
    await db_session.refresh(lst)
    return lst


@pytest_asyncio.fixture
async def task_list(db_session: AsyncSession, family_group, test_user):
    from app.models.task import TaskList
    lst = TaskList(name="Test Tasks", family_group_id=family_group.id, created_by=test_user.id)
    db_session.add(lst)
    await db_session.flush()
    await db_session.refresh(lst)
    return lst


@pytest_asyncio.fixture
async def budget(db_session: AsyncSession, family_group):
    from app.models.monthly_budget import MonthlyBudget
    from datetime import date
    today = date.today()
    b = MonthlyBudget(family_group_id=family_group.id, year=today.year, month=today.month)
    db_session.add(b)
    await db_session.flush()
    await db_session.refresh(b)
    return b