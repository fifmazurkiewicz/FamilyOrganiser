"""Transaction management service."""
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.account import Account
from app.models.transaction import (
    RecurringTransaction,
    Transaction,
    TransactionCategory,
    TransactionScope,
    TransactionTag,
    TransactionType,
)
from app.repositories.account import AccountRepository
from app.repositories.transaction import (
    CategoryRepository,
    RecurringTransactionRepository,
    TagRepository,
    TransactionRepository,
)
from app.services.exchange_rate import ExchangeRateService


class TransactionService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._tx = TransactionRepository(session)
        self._accounts = AccountRepository(session)
        self._categories = CategoryRepository(session)
        self._tags = TagRepository(session)
        self._recurring = RecurringTransactionRepository(session)
        self._fx = ExchangeRateService(session)

    async def _verify_account_access(self, account_id: UUID, user_id: UUID) -> Account:
        account = await self._accounts.get(account_id)
        if not account:
            raise NotFoundError("Account not found")
        if account.owner_id != user_id:
            joint = await self._accounts.get_joint_ownership(account_id, user_id)
            if not joint:
                raise ForbiddenError("Access denied to this account")
        return account

    async def create(
        self,
        user_id: UUID,
        *,
        account_id: UUID,
        category_id: Optional[UUID],
        family_group_id: Optional[UUID],
        transaction_type: TransactionType,
        scope: TransactionScope,
        amount: Decimal,
        currency: str,
        transaction_date: date,
        description: Optional[str],
        tag_ids: list[UUID],
        recurring_id: Optional[UUID],
    ) -> Transaction:
        account = await self._verify_account_access(account_id, user_id)

        amount_pln, exchange_rate = await self._fx.convert(amount, currency)

        tx = Transaction(
            user_id=user_id,
            account_id=account_id,
            category_id=category_id,
            family_group_id=family_group_id,
            transaction_type=transaction_type,
            scope=scope,
            amount=amount,
            currency=currency,
            amount_pln=amount_pln,
            exchange_rate=exchange_rate,
            transaction_date=transaction_date,
            description=description,
            recurring_id=recurring_id,
            is_recurring=recurring_id is not None,
        )
        self._session.add(tx)
        await self._session.flush()

        # Attach tags
        for tag_id in tag_ids:
            from sqlalchemy import select
            result = await self._session.execute(
                select(TransactionTag).where(
                    TransactionTag.id == tag_id,
                    TransactionTag.user_id == user_id,
                )
            )
            tag = result.scalar_one_or_none()
            if tag:
                tx.tags.append(tag)

        # Update account balance
        if transaction_type == TransactionType.EXPENSE:
            account.current_balance -= amount
        else:
            account.current_balance += amount

        await self._session.commit()
        await self._session.refresh(tx)
        return tx

    async def list(
        self,
        user_id: UUID,
        *,
        account_id: Optional[UUID] = None,
        category_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Transaction]:
        return await self._tx.list_for_user(
            user_id,
            account_id=account_id,
            category_id=category_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )

    async def get_owned(self, transaction_id: UUID, user_id: UUID) -> Transaction:
        from sqlalchemy import select

        result = await self._session.execute(
            select(Transaction).where(
                Transaction.id == transaction_id,
                Transaction.user_id == user_id,
            )
        )
        tx = result.scalar_one_or_none()
        if not tx:
            raise NotFoundError("Transaction not found")
        return tx

    async def update(
        self,
        tx: Transaction,
        *,
        category_id: Optional[UUID] = None,
        scope: Optional[TransactionScope] = None,
        amount: Optional[Decimal] = None,
        transaction_date: Optional[date] = None,
        description: Optional[str] = None,
    ) -> Transaction:
        if amount is not None and amount != tx.amount:
            account = await self._accounts.get(tx.account_id)
            if account:
                if tx.transaction_type == TransactionType.EXPENSE:
                    account.current_balance += tx.amount
                    account.current_balance -= amount
                else:
                    account.current_balance -= tx.amount
                    account.current_balance += amount
            tx.amount = amount

        if category_id is not None:
            tx.category_id = category_id
        if scope is not None:
            tx.scope = scope
        if transaction_date is not None:
            tx.transaction_date = transaction_date
        if description is not None:
            tx.description = description

        await self._session.commit()
        await self._session.refresh(tx)
        return tx

    async def delete(self, tx: Transaction) -> None:
        account = await self._accounts.get(tx.account_id)
        if account:
            if tx.transaction_type == TransactionType.EXPENSE:
                account.current_balance += tx.amount
            else:
                account.current_balance -= tx.amount

        await self._session.delete(tx)
        await self._session.commit()

    # ----------------------------------------------------------- categories

    async def list_categories(self, user_id: UUID) -> list[TransactionCategory]:
        return await self._categories.list_for_user(user_id)

    async def create_category(
        self,
        user_id: UUID,
        name: str,
        parent_id: Optional[UUID],
        icon: Optional[str],
        color: Optional[str],
    ) -> TransactionCategory:
        category = TransactionCategory(
            user_id=user_id,
            name=name,
            parent_id=parent_id,
            icon=icon,
            color=color,
        )
        self._session.add(category)
        await self._session.commit()
        await self._session.refresh(category)
        return category

    # --------------------------------------------------------------- tags

    async def list_tags(self, user_id: UUID) -> list[TransactionTag]:
        return await self._tags.list_for_user(user_id)

    async def create_tag(self, user_id: UUID, name: str) -> TransactionTag:
        tag = TransactionTag(user_id=user_id, name=name)
        self._session.add(tag)
        await self._session.commit()
        await self._session.refresh(tag)
        return tag

    # ------------------------------------------------------- recurring

    async def create_recurring(self, **kwargs) -> RecurringTransaction:
        recurring = RecurringTransaction(**kwargs)
        self._session.add(recurring)
        await self._session.commit()
        await self._session.refresh(recurring)
        return recurring

    async def list_recurring(self, user_id: UUID) -> list[RecurringTransaction]:
        return await self._recurring.list_active_for_user(user_id)
