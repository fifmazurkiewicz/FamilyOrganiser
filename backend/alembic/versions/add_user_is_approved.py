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
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {c["name"] for c in inspector.get_columns("users")}
    if "is_approved" not in columns:
        op.add_column(
            "users",
            sa.Column("is_approved", sa.Boolean(), nullable=True),
        )
    op.execute(sa.text("UPDATE users SET is_approved = true WHERE is_approved IS NULL"))
    op.alter_column(
        "users",
        "is_approved",
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=sa.false(),
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {c["name"] for c in inspector.get_columns("users")}
    if "is_approved" in columns:
        op.drop_column("users", "is_approved")
