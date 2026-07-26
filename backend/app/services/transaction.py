"""Transaction management service."""
from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.transaction import (
    RecurringTransaction, Transaction, TransactionCategory, TransactionTag
)


class TransactionService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

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

    async def list(self, user_id: UUID, *, limit: int = 50, offset: int = 0) -> List[Transaction]:
        return await self.list_for_user(user_id, limit=limit, offset=offset)

    async def get(self, transaction_id: UUID, user_id: UUID) -> Transaction:
        result = await self._session.execute(
            select(Transaction).where(
                Transaction.id == transaction_id,
                Transaction.user_id == user_id,
            )
        )
        transaction = result.scalar_one_or_none()
        if not transaction:
            raise NotFoundError("Transaction not found")
        return transaction

    async def create(self, data: dict) -> Transaction:
        transaction = Transaction(
            user_id=data["user_id"],
            account_id=data["account_id"],
            category_id=data.get("category_id"),
            family_group_id=data.get("family_group_id"),
            transaction_type=data["transaction_type"],
            scope=data.get("scope", "personal"),
            amount=data["amount"],
            currency=data.get("currency", "PLN"),
            amount_pln=data.get("amount_pln"),
            exchange_rate=data.get("exchange_rate"),
            transaction_date=data["transaction_date"],
            description=data.get("description"),
            receipt_url=data.get("receipt_url"),
        )
        self._session.add(transaction)
        if "tag_ids" in data:
            for tag_id in data["tag_ids"]:
                tag_result = await self._session.execute(select(TransactionTag).where(TransactionTag.id == tag_id))
                tag = tag_result.scalar_one_or_none()
                if tag:
                    transaction.tags.append(tag)
        await self._session.commit()
        await self._session.refresh(transaction)
        return transaction

    async def update(self, transaction: Transaction, data: dict) -> Transaction:
        for key, value in data.items():
            if key != "tag_ids" and value is not None and hasattr(transaction, key):
                setattr(transaction, key, value)
        if "tag_ids" in data:
            transaction.tags.clear()
            for tag_id in data["tag_ids"]:
                tag_result = await self._session.execute(select(TransactionTag).where(TransactionTag.id == tag_id))
                tag = tag_result.scalar_one_or_none()
                if tag:
                    transaction.tags.append(tag)
        await self._session.commit()
        await self._session.refresh(transaction)
        return transaction

    async def delete(self, transaction: Transaction) -> None:
        await self._session.delete(transaction)
        await self._session.commit()

    # Categories
    async def list_categories(self, user_id: UUID) -> List[TransactionCategory]:
        result = await self._session.execute(
            select(TransactionCategory).where(
                (TransactionCategory.user_id == user_id)
                | (TransactionCategory.is_system == True)
            )
        )
        return list(result.scalars().all())

    async def create_category(self, data: dict, user_id: UUID) -> TransactionCategory:
        category = TransactionCategory(
            user_id=user_id,
            parent_id=data.get("parent_id"),
            name=data["name"],
            icon=data.get("icon"),
            color=data.get("color"),
            is_system=False,
        )
        self._session.add(category)
        await self._session.commit()
        await self._session.refresh(category)
        return category

    async def delete_category(self, category_id: UUID) -> None:
        category = await self._session.get(TransactionCategory, category_id)
        if not category:
            raise NotFoundError("Category not found")
        await self._session.delete(category)
        await self._session.commit()

    # Tags
    async def list_tags(self, user_id: UUID) -> List[TransactionTag]:
        result = await self._session.execute(
            select(TransactionTag).where(TransactionTag.user_id == user_id)
        )
        return list(result.scalars().all())

    async def create_tag(self, data: dict, user_id: UUID) -> TransactionTag:
        tag = TransactionTag(user_id=user_id, name=data["name"])
        self._session.add(tag)
        await self._session.commit()
        await self._session.refresh(tag)
        return tag

    async def delete_tag(self, tag_id: UUID) -> None:
        tag = await self._session.get(TransactionTag, tag_id)
        if not tag:
            raise NotFoundError("Tag not found")
        await self._session.delete(tag)
        await self._session.commit()

    # Recurring
    async def list_active_recurring(self, user_id: UUID) -> List[RecurringTransaction]:
        result = await self._session.execute(
            select(RecurringTransaction).where(
                RecurringTransaction.user_id == user_id,
                RecurringTransaction.is_active == True,
            )
        )
        return list(result.scalars().all())

    async def list_all_active_recurring(self) -> List[RecurringTransaction]:
        result = await self._session.execute(
            select(RecurringTransaction).where(RecurringTransaction.is_active == True)
        )
        return list(result.scalars().all())

    async def create_recurring(self, data: dict) -> RecurringTransaction:
        recurring = RecurringTransaction(
            user_id=data["user_id"],
            account_id=data["account_id"],
            category_id=data.get("category_id"),
            name=data["name"],
            amount=data["amount"],
            currency=data.get("currency", "PLN"),
            transaction_type=data["transaction_type"],
            frequency=data.get("frequency", "monthly"),
            day_of_month=data["day_of_month"],
            reminder_days_before=data.get("reminder_days_before", 3),
            total_occurrences=data.get("total_occurrences"),
            start_date=data["start_date"],
            end_date=data.get("end_date"),
            description=data.get("description"),
        )
        self._session.add(recurring)
        await self._session.commit()
        await self._session.refresh(recurring)
        return recurring
