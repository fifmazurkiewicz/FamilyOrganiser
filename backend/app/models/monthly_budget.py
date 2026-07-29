import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid
from app.db.base import Base


class BudgetEntryType(str, PyEnum):
    INCOME = "income"
    EXPENSE = "expense"


class MonthlyBudget(Base):
    __tablename__ = "monthly_budgets"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    family_group_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("family_groups.id", ondelete="CASCADE"), nullable=False
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    entries: Mapped[list["BudgetEntry"]] = relationship(
        "BudgetEntry", back_populates="budget", cascade="all, delete-orphan"
    )


class BudgetEntry(Base):
    __tablename__ = "monthly_budget_entries"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    budget_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("monthly_budgets.id", ondelete="CASCADE"), nullable=False
    )
    entry_type: Mapped[BudgetEntryType] = mapped_column(
        Enum(BudgetEntryType, native_enum=False), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    budget: Mapped["MonthlyBudget"] = relationship("MonthlyBudget", back_populates="entries")