"""Add frequency to recurring_transactions

Revision ID: add_recurring_freq
Revises:
Create Date: 2026-03-08

Uruchom: cd backend && poetry run alembic upgrade head
"""
from alembic import op
import sqlalchemy as sa

revision = "add_recurring_freq"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Użyj VARCHAR zamiast ENUM - prostsza migracja, działa bez tworzenia typu
    op.add_column(
        "recurring_transactions",
        sa.Column("frequency", sa.String(20), server_default="monthly", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("recurring_transactions", "frequency")
