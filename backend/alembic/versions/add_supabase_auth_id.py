"""Add supabase_auth_id; make hashed_password nullable for Supabase Auth.

Revision ID: add_supabase_auth_id
Revises: add_family_organiser_modules
Create Date: 2026-07-28
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "add_supabase_auth_id"
down_revision = "add_family_organiser_modules"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("supabase_auth_id", UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_users_supabase_auth_id", "users", ["supabase_auth_id"], unique=True)
    op.alter_column("users", "hashed_password", existing_type=sa.String(255), nullable=True)


def downgrade() -> None:
    op.alter_column("users", "hashed_password", existing_type=sa.String(255), nullable=False)
    op.drop_index("ix_users_supabase_auth_id", table_name="users")
    op.drop_column("users", "supabase_auth_id")
