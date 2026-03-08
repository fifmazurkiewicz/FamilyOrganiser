from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import RecurringTransaction, Transaction, TransactionCategory, TransactionTag
from app.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    model = Transaction

    async def list_for_user(
        self,
        user_id: UUID,
        *,
        account_id: Optional[UUID] = None,
        category_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Transaction]:
        conditions = [Transaction.user_id == user_id]
        if account_id:
            conditions.append(Transaction.account_id == account_id)
        if category_id:
            conditions.append(Transaction.category_id == category_id)
        if start_date:
            conditions.append(Transaction.transaction_date >= start_date)
        if end_date:
            conditions.append(Transaction.transaction_date <= end_date)

        result = await self._session.execute(
            select(Transaction)
            .where(and_(*conditions))
            .order_by(Transaction.transaction_date.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())


class CategoryRepository(BaseRepository[TransactionCategory]):
    model = TransactionCategory

    async def list_for_user(self, user_id: UUID) -> List[TransactionCategory]:
        result = await self._session.execute(
            select(TransactionCategory).where(
                (TransactionCategory.user_id == user_id)
                | (TransactionCategory.is_system == True)
            )
        )
        return list(result.scalars().all())


class TagRepository(BaseRepository[TransactionTag]):
    model = TransactionTag

    async def list_for_user(self, user_id: UUID) -> List[TransactionTag]:
        result = await self._session.execute(
            select(TransactionTag).where(TransactionTag.user_id == user_id)
        )
        return list(result.scalars().all())


class RecurringTransactionRepository(BaseRepository[RecurringTransaction]):
    model = RecurringTransaction

    async def list_active_for_user(self, user_id: UUID) -> List[RecurringTransaction]:
        result = await self._session.execute(
            select(RecurringTransaction).where(
                RecurringTransaction.user_id == user_id,
                RecurringTransaction.is_active == True,
            )
        )
        return list(result.scalars().all())

    async def list_all_active(self) -> List[RecurringTransaction]:
        result = await self._session.execute(
            select(RecurringTransaction).where(RecurringTransaction.is_active == True)
        )
        return list(result.scalars().all())
