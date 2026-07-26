import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid, JSON
from app.db.base import Base


class NotificationType(str, PyEnum):
    BUDGET_ALERT = "budget_alert"
    GOAL_ACHIEVED = "goal_achieved"
    GOAL_REMINDER = "goal_reminder"
    RECURRING_REMINDER = "recurring_reminder"
    RECURRING_UNCONFIRMED = "recurring_unconfirmed"
    DEPOSIT_MATURITY = "deposit_maturity"
    BOND_MATURITY = "bond_maturity"
    WEEKLY_SUMMARY = "weekly_summary"
    GROUP_REMOVED = "group_removed"
    PASSWORD_RESET = "password_reset"
    APPROVAL_REQUEST = "approval_request"
    APPROVAL_RESOLVED = "approval_resolved"
    JOINT_ACCOUNT_TRANSACTION = "joint_account_transaction"
    ADMIN_PASSWORD_RESET = "admin_password_reset"
    SHOPPING_ITEM_ADDED = "shopping_item_added"
    SHOPPING_ITEM_BOUGHT = "shopping_item_bought"
    TASK_COMPLETED = "task_completed"
    BUDGET_EXCEEDED = "budget_exceeded"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    notification_type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="notifications")
