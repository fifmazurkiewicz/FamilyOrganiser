import uuid
from datetime import datetime, date, timezone
from enum import Enum as PyEnum
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum, Numeric, Date, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid
from app.db.base import Base


class IncomeCategory(str, PyEnum):
    SALARY = "salary"
    BONUS = "bonus"
    FREELANCE = "freelance"
    RENTAL = "rental"
    DIVIDEND = "dividend"
    SALE = "sale"
    OTHER = "other"


class IncomeTemplate(Base):
    """Recurring income template (e.g. monthly salary)."""
    __tablename__ = "income_templates"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("accounts.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    base_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="PLN")
    category: Mapped[IncomeCategory] = mapped_column(Enum(IncomeCategory), default=IncomeCategory.SALARY)
    day_of_month: Mapped[int] = mapped_column(Integer, nullable=False)  # 1–31
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    incomes: Mapped[list["Income"]] = relationship("Income", back_populates="template")


class Income(Base):
    """Actual income entry per month."""
    __tablename__ = "incomes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("accounts.id"), nullable=False
    )
    template_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("income_templates.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    base_amount: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="PLN")
    category: Mapped[IncomeCategory] = mapped_column(Enum(IncomeCategory), default=IncomeCategory.SALARY)
    income_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_modified: Mapped[bool] = mapped_column(Boolean, default=False)  # amount differs from base
    is_skipped: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    template: Mapped["IncomeTemplate | None"] = relationship("IncomeTemplate", back_populates="incomes")
