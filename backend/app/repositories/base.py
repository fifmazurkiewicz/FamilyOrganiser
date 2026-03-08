"""Generic async repository pattern for SQLAlchemy 2.0."""
from typing import Any, Generic, Sequence, Type, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    model: Type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, id: UUID) -> ModelT | None:
        return await self._session.get(self.model, id)

    async def get_or_raise(self, id: UUID) -> ModelT:
        from app.core.exceptions import NotFoundError

        obj = await self.get(id)
        if obj is None:
            raise NotFoundError(f"{self.model.__name__} {id} not found")
        return obj

    async def list(self, *filters: Any, limit: int = 100, offset: int = 0) -> Sequence[ModelT]:
        stmt = select(self.model).where(*filters).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def add(self, obj: ModelT) -> ModelT:
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def delete(self, obj: ModelT) -> None:
        await self._session.delete(obj)
        await self._session.flush()

    async def commit(self) -> None:
        await self._session.commit()
