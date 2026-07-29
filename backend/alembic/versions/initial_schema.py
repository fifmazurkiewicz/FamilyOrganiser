"""Initial schema: users, family groups, notifications, audit, exchange rates.

Revision ID: initial_schema
Revises:
Create Date: 2026-07-30
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "initial_schema"
down_revision = "reset_public_once"
branch_labels = None
depends_on = None

family_role = sa.Enum("admin", "member", name="familyrole")
notification_type = sa.Enum(
    "budget_alert",
    "goal_achieved",
    "goal_reminder",
    "recurring_reminder",
    "recurring_unconfirmed",
    "deposit_maturity",
    "bond_maturity",
    "weekly_summary",
    "group_removed",
    "password_reset",
    "approval_request",
    "approval_resolved",
    "joint_account_transaction",
    "admin_password_reset",
    "shopping_item_added",
    "shopping_item_bought",
    "task_completed",
    "budget_exceeded",
    name="notificationtype",
)


def upgrade() -> None:
    family_role.create(op.get_bind(), checkfirst=True)
    notification_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=True),
        sa.Column("supabase_auth_id", UUID(as_uuid=True), nullable=True),
        sa.Column("full_name", sa.String(100), nullable=False),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("default_currency", sa.String(3), nullable=False, server_default="PLN"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_app_admin", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_locked", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("security_question_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_supabase_auth_id", "users", ["supabase_auth_id"], unique=True)

    op.create_table(
        "security_questions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("hashed_answer", sa.String(255), nullable=False),
    )

    op.create_table(
        "family_groups",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "family_memberships",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "family_group_id",
            UUID(as_uuid=True),
            sa.ForeignKey("family_groups.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", family_role, nullable=False, server_default="member"),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("share_expenses", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("share_investments", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("share_savings", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("share_budget", sa.Boolean(), nullable=False, server_default="false"),
    )

    op.create_table(
        "invitation_links",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("token", sa.String(64), nullable=False),
        sa.Column(
            "family_group_id",
            UUID(as_uuid=True),
            sa.ForeignKey("family_groups.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_by_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("single_use", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("used", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_invitation_links_token", "invitation_links", ["token"], unique=True)

    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("notification_type", notification_type, nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "exchange_rates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("rate_date", sa.Date(), nullable=False),
        sa.Column("rate_to_pln", sa.Numeric(10, 6), nullable=False),
        sa.Column("source", sa.String(50), nullable=False, server_default="NBP"),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("currency", "rate_date", name="uq_exchange_rate_currency_date"),
    )
    op.create_index("ix_exchange_rates_currency", "exchange_rates", ["currency"])
    op.create_index("ix_exchange_rates_rate_date", "exchange_rates", ["rate_date"])

    op.create_table(
        "audit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "actor_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "target_user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "family_group_id",
            UUID(as_uuid=True),
            sa.ForeignKey("family_groups.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=True),
        sa.Column("resource_id", sa.String(36), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("exchange_rates")
    op.drop_table("notifications")
    op.drop_index("ix_invitation_links_token", table_name="invitation_links")
    op.drop_table("invitation_links")
    op.drop_table("family_memberships")
    op.drop_table("family_groups")
    op.drop_table("security_questions")
    op.drop_index("ix_users_supabase_auth_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    notification_type.drop(op.get_bind(), checkfirst=True)
    family_role.drop(op.get_bind(), checkfirst=True)
