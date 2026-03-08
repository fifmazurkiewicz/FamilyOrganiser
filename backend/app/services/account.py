"""Account management service."""
from datetime import date
from decimal import Decimal
from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.account import Account, AccountType, JointAccountOwner
from app.models.transaction import Transaction, TransactionScope, TransactionType
from app.repositories.account import AccountRepository


class AccountService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._accounts = AccountRepository(session)

    async def get_accessible(self, account_id: UUID, user_id: UUID) -> Account:
        account = await self._accounts.get(account_id)
        if not account:
            raise NotFoundError("Account not found")
        if account.owner_id != user_id:
            joint = await self._accounts.get_joint_ownership(account_id, user_id)
            if not joint:
                raise ForbiddenError("Access denied to this account")
        return account

    async def require_owner(self, account_id: UUID, user_id: UUID) -> Account:
        account = await self.get_accessible(account_id, user_id)
        if account.owner_id != user_id:
            raise ForbiddenError("Only the account owner can perform this action")
        return account

    async def list_all(self, user_id: UUID) -> List[Account]:
        owned = await self._accounts.list_by_owner(user_id)
        owned_ids = {a.id for a in owned}

        joint_ownerships = await self._accounts.list_joint_accounts(user_id)
        extra: List[Account] = []
        for jo in joint_ownerships:
            if jo.account_id not in owned_ids:
                acc = await self._accounts.get(jo.account_id)
                if acc and acc.is_active:
                    extra.append(acc)

        return list(owned) + extra

    async def create(
        self,
        owner_id: UUID,
        *,
        name: str,
        account_type: AccountType,
        currency: str,
        color: str | None,
        icon: str | None,
        initial_balance: Decimal,
        opening_date: date | None,
        is_joint: bool,
        is_visible_to_family: bool,
        share_transactions_with_family: bool,
        credit_limit: Decimal | None,
        statement_day: int | None,
        payment_due_day: int | None,
    ) -> Account:
        account = Account(
            owner_id=owner_id,
            name=name,
            account_type=account_type,
            currency=currency,
            color=color,
            icon=icon,
            initial_balance=initial_balance,
            current_balance=initial_balance,
            opening_date=opening_date,
            is_joint=is_joint,
            is_visible_to_family=is_visible_to_family,
            share_transactions_with_family=share_transactions_with_family,
            credit_limit=credit_limit,
            statement_day=statement_day,
            payment_due_day=payment_due_day,
        )
        self._session.add(account)
        await self._session.commit()
        await self._session.refresh(account)
        return account

    async def update(self, account: Account, **fields) -> Account:
        for key, value in fields.items():
            if value is not None and hasattr(account, key):
                setattr(account, key, value)
        await self._session.commit()
        await self._session.refresh(account)
        return account

    async def deactivate(self, account: Account) -> None:
        from app.core.exceptions import BusinessLogicError

        if account.is_joint:
            raise BusinessLogicError(
                "Joint accounts require an approval request from all owners before deletion"
            )
        account.is_active = False
        await self._session.commit()

    async def correct_balance(
        self, account: Account, user_id: UUID, actual_balance: Decimal, note: str | None
    ) -> Account:
        diff = actual_balance - account.current_balance
        account.current_balance = actual_balance

        if diff != Decimal("0"):
            correction = Transaction(
                user_id=user_id,
                account_id=account.id,
                transaction_type=TransactionType.INCOME if diff > 0 else TransactionType.EXPENSE,
                scope=TransactionScope.PERSONAL,
                amount=abs(diff),
                currency=account.currency,
                transaction_date=date.today(),
                description=f"Korekta salda{f': {note}' if note else ''}",
            )
            self._session.add(correction)

        await self._session.commit()
        await self._session.refresh(account)
        return account

    async def add_joint_owner(
        self, account: Account, user_id: UUID, notify_on_transaction: bool
    ) -> JointAccountOwner:
        existing = await self._accounts.get_joint_ownership(account.id, user_id)
        if existing:
            raise ConflictError("User is already a joint owner of this account")

        joint = JointAccountOwner(
            account_id=account.id,
            user_id=user_id,
            notify_on_transaction=notify_on_transaction,
        )
        self._session.add(joint)
        account.is_joint = True
        await self._session.commit()
        return joint
