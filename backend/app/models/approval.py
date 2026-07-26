import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import String, DateTime, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid
from app.db.base import Base


class ApprovalStatus(str, PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"


class ApprovalActionType(str, PyEnum):
    DELETE_JOINT_ACCOUNT = "delete_joint_account"
    DELETE_SHARED_WALLET = "delete_shared_wallet"
    DELETE_SHARED_TRANSACTION = "delete_shared_transaction"
    EDIT_SHARED_TRANSACTION = "edit_shared_transaction"


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    initiator_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    family_group_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("family_groups.id"), nullable=False
    )
    action_type: Mapped[ApprovalActionType] = mapped_column(Enum(ApprovalActionType), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ApprovalStatus] = mapped_column(
        Enum(ApprovalStatus), default=ApprovalStatus.PENDING
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    initiator: Mapped["User"] = relationship("User")
    votes: Mapped[list["ApprovalVote"]] = relationship(
        "ApprovalVote", back_populates="request", cascade="all, delete-orphan"
    )


class ApprovalVote(Base):
    __tablename__ = "approval_votes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    request_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("approval_requests.id", ondelete="CASCADE"), nullable=False
    )
    voter_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    approved: Mapped[bool] = mapped_column(Boolean, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    voted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    request: Mapped["ApprovalRequest"] = relationship("ApprovalRequest", back_populates="votes")
    voter: Mapped["User"] = relationship("User")
