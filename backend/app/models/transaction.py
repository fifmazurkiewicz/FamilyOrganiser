import uuid
from datetime import datetime, date, timezone
from enum import Enum as PyEnum
from decimal import Decimal
from sqlalchemy import (
    String, Boolean, DateTime, ForeignKey, Enum, Numeric, Date, Text, Integer, Table, Column
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid
from app.db.base import Base


class TransactionType(str, PyEnum):
    EXPENSE = "expense"
    INCOME = "income"


class TransactionScope(str, PyEnum):
    PERSONAL = "personal"
    FAMILY = "family"
    SHARED = "shared"


# Many-to-many: transactions <-> tags
transaction_tag_association = Table(
    "transaction_tag_associations",
    Base.metadata,
    Column("transaction_id", Uuid, ForeignKey("transactions.id", ondelete="CASCADE")),
    Column("tag_id", Uuid, ForeignKey("transaction_tags.id", ondelete="CASCADE")),
)


class TransactionCategory(Base):
    __tablename__ = "transaction_categories"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )  # None = system default
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("transaction_categories.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)

    subcategories: Mapped[list["TransactionCategory"]] = relationship(
        "TransactionCategory", back_populates="parent"
    )
    parent: Mapped["TransactionCategory | None"] = relationship(
        "TransactionCategory", back_populates="subcategories", remote_side=[id]
    )


class TransactionTag(Base):
    __tablename__ = "transaction_tags"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", secondary=transaction_tag_association, back_populates="tags"
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("transaction_categories.id"), nullable=True
    )
    family_group_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("family_groups.id"), nullable=True
    )

    transaction_type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType), nullable=False
    )
    scope: Mapped[TransactionScope] = mapped_column(
        Enum(TransactionScope), default=TransactionScope.PERSONAL
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="PLN")
    amount_pln: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    exchange_rate: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    receipt_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurring_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("recurring_transactions.id"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    account: Mapped["Account"] = relationship(
        "Account", back_populates="transactions", foreign_keys=[account_id]
    )
    category: Mapped["TransactionCategory | None"] = relationship("TransactionCategory")
    tags: Mapped[list["TransactionTag"]] = relationship(
        "TransactionTag", secondary=transaction_tag_association, back_populates="transactions"
    )
    user: Mapped["User"] = relationship("User")


class RecurringFrequency(str, PyEnum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"


class RecurringTransaction(Base):
    __tablename__ = "recurring_transactions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("accounts.id"), nullable=False
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("transaction_categories.id"), nullable=True
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="PLN")
    transaction_type: Mapped[TransactionType] = mapped_column(Enum(TransactionType))
    frequency: Mapped[RecurringFrequency] = mapped_column(
        Enum(RecurringFrequency), default=RecurringFrequency.MONTHLY
    )
    day_of_month: Mapped[int] = mapped_column(Integer, nullable=False)  # 1–31 (dla monthly)
    reminder_days_before: Mapped[int] = mapped_column(Integer, default=3)
    total_occurrences: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_occurrence: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
