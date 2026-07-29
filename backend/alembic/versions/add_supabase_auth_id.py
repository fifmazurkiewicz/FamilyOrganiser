"""Legacy no-op (supabase_auth_id in initial_schema).

Revision ID: add_supabase_auth_id
Revises: add_family_organiser_modules
Create Date: 2026-07-28
"""
from alembic import op

revision = "add_supabase_auth_id"
down_revision = "add_family_organiser_modules"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
