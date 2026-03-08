import uuid
from datetime import datetime, date, timezone
from enum import Enum as PyEnum
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum, Numeric, Date, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from decimal import Decimal


class AccountType(str, PyEnum):
    BANK_INDIVIDUAL = "bank_individual"
    BANK_JOINT = "bank_joint"
    PREPAID_EWALLET = "prepaid_ewallet"
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    SAVINGS = "savings"
    CRYPTO_EXCHANGE = "crypto_exchange"


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    account_type: Mapped[AccountType] = mapped_column(Enum(AccountType), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="PLN", nullable=False)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)  # hex color
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    initial_balance: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"))
    current_balance: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"))
    opening_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_joint: Mapped[bool] = mapped_column(Boolean, default=False)
    is_visible_to_family: Mapped[bool] = mapped_column(Boolean, default=False)
    share_transactions_with_family: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Credit card specific
    credit_limit: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    statement_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    payment_due_day: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    owner: Mapped["User"] = relationship("User", back_populates="accounts", foreign_keys=[owner_id])
    joint_owners: Mapped[list["JointAccountOwner"]] = relationship(
        "JointAccountOwner", back_populates="account", cascade="all, delete-orphan"
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="account", foreign_keys="Transaction.account_id"
    )


class JointAccountOwner(Base):
    __tablename__ = "joint_account_owners"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    notify_on_transaction: Mapped[bool] = mapped_column(Boolean, default=True)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    account: Mapped["Account"] = relationship("Account", back_populates="joint_owners")
    user: Mapped["User"] = relationship("User")
