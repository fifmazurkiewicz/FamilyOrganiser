import uuid
from datetime import datetime, date, timezone
from enum import Enum as PyEnum
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum, Numeric, Date, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid
from app.db.base import Base


class GoalType(str, PyEnum):
    PERSONAL = "personal"
    FAMILY = "family"


class GoalVisibility(str, PyEnum):
    PUBLIC = "public"
    PRIVATE = "private"


class SavingsGoal(Base):
    __tablename__ = "savings_goals"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    family_group_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("family_groups.id"), nullable=True
    )
    linked_account_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("accounts.id"), nullable=True
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)

    target_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    current_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"))
    currency: Mapped[str] = mapped_column(String(3), default="PLN")

    goal_type: Mapped[GoalType] = mapped_column(Enum(GoalType), default=GoalType.PERSONAL)
    visibility: Mapped[GoalVisibility] = mapped_column(
        Enum(GoalVisibility), default=GoalVisibility.PRIVATE
    )

    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    monthly_contribution: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    contributions: Mapped[list["SavingsContribution"]] = relationship(
        "SavingsContribution", back_populates="goal", cascade="all, delete-orphan"
    )
    members: Mapped[list["SavingsGoalMember"]] = relationship(
        "SavingsGoalMember", back_populates="goal", cascade="all, delete-orphan"
    )


class SavingsContribution(Base):
    __tablename__ = "savings_contributions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    goal_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("savings_goals.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    source_account_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("accounts.id"), nullable=True
    )

    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="PLN")
    contribution_date: Mapped[date] = mapped_column(Date, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_withdrawal: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    goal: Mapped["SavingsGoal"] = relationship("SavingsGoal", back_populates="contributions")
    user: Mapped["User"] = relationship("User")


class SavingsGoalMember(Base):
    __tablename__ = "savings_goal_members"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    goal_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("savings_goals.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    goal: Mapped["SavingsGoal"] = relationship("SavingsGoal", back_populates="members")
    user: Mapped["User"] = relationship("User")
