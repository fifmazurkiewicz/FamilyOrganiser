"""ONE-TIME: wyczyść public schema przed pełnym baseline (usuń po udanym deployu).

Revision ID: reset_public_once
Revises:
Create Date: 2026-07-30
"""
from alembic import op

revision = "reset_public_once"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS public CASCADE")
    op.execute("CREATE SCHEMA public")
    op.execute("GRANT ALL ON SCHEMA public TO postgres")
    op.execute("GRANT ALL ON SCHEMA public TO public")
    op.execute("GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role")
    op.execute("GRANT ALL ON SCHEMA public TO service_role")


def downgrade() -> None:
    pass
