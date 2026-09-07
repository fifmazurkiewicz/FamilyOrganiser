"""Add users.is_approved and grandfather existing rows.

Revision ID: add_user_is_approved
Revises: add_supabase_auth_id
Create Date: 2026-09-07
"""
import sqlalchemy as sa

from alembic import op

revision = "add_user_is_approved"
down_revision = "add_supabase_auth_id"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_approved", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.execute(sa.text("UPDATE users SET is_approved = true"))
    op.alter_column(
        "users",
        "is_approved",
        existing_type=sa.Boolean(),
        existing_nullable=False,
        server_default="false",
    )


def downgrade() -> None:
    op.drop_column("users", "is_approved")
