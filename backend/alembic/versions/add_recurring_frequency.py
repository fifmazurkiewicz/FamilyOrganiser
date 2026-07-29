"""Legacy no-op (recurring_transactions removed from app).

Revision ID: add_recurring_freq
Revises: initial_schema
Create Date: 2026-03-08
"""
from alembic import op

revision = "add_recurring_freq"
down_revision = "initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
