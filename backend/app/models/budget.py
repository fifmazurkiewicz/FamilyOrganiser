import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum
from decimal import Decimal
from sqlalchemy import String, DateTime, ForeignKey, Enum, Numeric, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid
from app.db.base import Base


class BudgetScope(str, PyEnum):
    PERSONAL = "personal"
    FAMILY = "family"


class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    family_group_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("family_groups.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    scope: Mapped[BudgetScope] = mapped_column(Enum(BudgetScope), default=BudgetScope.PERSONAL)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int | None] = mapped_column(Integer, nullable=True)  # None = annual budget
    alert_threshold_percent: Mapped[int] = mapped_column(Integer, default=80)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    categories: Mapped[list["BudgetCategory"]] = relationship(
        "BudgetCategory", back_populates="budget", cascade="all, delete-orphan"
    )


class BudgetCategory(Base):
    __tablename__ = "budget_categories"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    budget_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("transaction_categories.id"), nullable=False
    )
    planned_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="PLN")

    budget: Mapped["Budget"] = relationship("Budget", back_populates="categories")
    category: Mapped["TransactionCategory"] = relationship("TransactionCategory")
