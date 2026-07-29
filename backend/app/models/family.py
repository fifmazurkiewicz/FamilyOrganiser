import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid
from app.db.base import Base


class FamilyRole(str, PyEnum):
    ADMIN = "admin"
    MEMBER = "member"


class FamilyGroup(Base):
    __tablename__ = "family_groups"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    memberships: Mapped[list["FamilyMembership"]] = relationship(
        "FamilyMembership", back_populates="family_group", cascade="all, delete-orphan"
    )
    invitation_links: Mapped[list["InvitationLink"]] = relationship(
        "InvitationLink", back_populates="family_group", cascade="all, delete-orphan"
    )


class FamilyMembership(Base):
    __tablename__ = "family_memberships"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    family_group_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("family_groups.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[FamilyRole] = mapped_column(
        Enum(FamilyRole, native_enum=False), default=FamilyRole.MEMBER, nullable=False
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Sharing preferences
    share_expenses: Mapped[bool] = mapped_column(Boolean, default=False)
    share_investments: Mapped[bool] = mapped_column(Boolean, default=False)
    share_savings: Mapped[bool] = mapped_column(Boolean, default=False)
    share_budget: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship("User", back_populates="memberships")
    family_group: Mapped["FamilyGroup"] = relationship("FamilyGroup", back_populates="memberships")


class InvitationLink(Base):
    __tablename__ = "invitation_links"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    family_group_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("family_groups.id", ondelete="CASCADE"), nullable=False
    )
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    single_use: Mapped[bool] = mapped_column(Boolean, default=True)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    family_group: Mapped["FamilyGroup"] = relationship(
        "FamilyGroup", back_populates="invitation_links"
    )
