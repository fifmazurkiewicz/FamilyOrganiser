import uuid
from datetime import datetime, date, timezone
from enum import Enum as PyEnum
from decimal import Decimal
from sqlalchemy import String, DateTime, ForeignKey, Enum, Numeric, Date, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class SimpleInvestmentType(str, PyEnum):
    DEPOSIT = "deposit"
    BONDS = "bonds"
    STOCKS = "stocks"
    OTHER = "other"


class InterestPeriod(str, PyEnum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class DurationUnit(str, PyEnum):
    MONTHS = "months"
    QUARTERS = "quarters"
    YEARS = "years"


class SimpleInvestment(Base):
    __tablename__ = "simple_investments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("family_groups.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    investment_type: Mapped[SimpleInvestmentType] = mapped_column(
        Enum(SimpleInvestmentType), nullable=False
    )
    principal_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    interest_rate: Mapped[Decimal] = mapped_column(
        Numeric(6, 4), nullable=False
    )  # percentage as decimal, e.g. 0.05 = 5%
    interest_period: Mapped[InterestPeriod] = mapped_column(
        Enum(InterestPeriod), default=InterestPeriod.YEARLY
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    duration_value: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_unit: Mapped[DurationUnit] = mapped_column(
        Enum(DurationUnit), default=DurationUnit.MONTHS
    )
    end_date: Mapped[date] = mapped_column(Date, nullable=True)
    projected_profit: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=True
    )
    projected_total: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )