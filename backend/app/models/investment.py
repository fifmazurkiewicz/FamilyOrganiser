import uuid
from datetime import datetime, date, timezone
from enum import Enum as PyEnum
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum, Numeric, Date, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid
from app.db.base import Base


class InvestmentType(str, PyEnum):
    STOCK = "stock"
    ETF = "etf"
    FUND = "fund"
    REAL_ESTATE = "real_estate"
    CRYPTO = "crypto"
    POLISH_BOND = "polish_bond"
    BANK_DEPOSIT = "bank_deposit"


class BondType(str, PyEnum):
    OFL = "OFL"   # 3-month fixed
    ROR = "ROR"   # 1-year variable (ref rate)
    DOR = "DOR"   # 2-year variable (ref rate)
    TOS = "TOS"   # 3-year fixed
    COI = "COI"   # 4-year variable (CPI)
    EDO = "EDO"   # 10-year variable (CPI)
    ROS = "ROS"   # 6-year family
    ROD = "ROD"   # 12-year family


class Investment(Base):
    __tablename__ = "investments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    investment_type: Mapped[InvestmentType] = mapped_column(Enum(InvestmentType), nullable=False)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    ticker: Mapped[str | None] = mapped_column(String(20), nullable=True)
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(20, 8), nullable=True)
    purchase_price: Mapped[Decimal | None] = mapped_column(Numeric(15, 4), nullable=True)
    current_price: Mapped[Decimal | None] = mapped_column(Numeric(15, 4), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="PLN")
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_shared: Mapped[bool] = mapped_column(Boolean, default=False)

    # Real estate specific
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    rental_income_monthly: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)

    # Bank deposit specific
    interest_rate: Mapped[Decimal | None] = mapped_column(Numeric(6, 4), nullable=True)
    maturity_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    bank_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class PolishBond(Base):
    __tablename__ = "polish_bonds"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    bond_type: Mapped[BondType] = mapped_column(Enum(BondType), nullable=False)
    series: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g. EDO0336
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)  # number of units (1 unit = 100 PLN)
    purchase_date: Mapped[date] = mapped_column(Date, nullable=False)
    maturity_date: Mapped[date] = mapped_column(Date, nullable=False)
    first_period_rate: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)  # e.g. 0.0630 = 6.30%
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User")
