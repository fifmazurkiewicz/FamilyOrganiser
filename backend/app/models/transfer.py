import uuid
from datetime import datetime, date, timezone
from enum import Enum as PyEnum
from decimal import Decimal
from sqlalchemy import String, DateTime, ForeignKey, Enum, Numeric, Date, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid
from app.db.base import Base


class TransferType(str, PyEnum):
    ACCOUNT_TO_ACCOUNT = "account_to_account"
    ACCOUNT_TO_GOAL = "account_to_goal"
    GOAL_TO_ACCOUNT = "goal_to_account"
    GOAL_TO_GOAL = "goal_to_goal"


class Transfer(Base):
    __tablename__ = "transfers"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    transfer_type: Mapped[TransferType] = mapped_column(Enum(TransferType), nullable=False)

    from_account_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("accounts.id"), nullable=True
    )
    to_account_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("accounts.id"), nullable=True
    )
    from_goal_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("savings_goals.id"), nullable=True
    )
    to_goal_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("savings_goals.id"), nullable=True
    )

    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="PLN")
    transfer_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
