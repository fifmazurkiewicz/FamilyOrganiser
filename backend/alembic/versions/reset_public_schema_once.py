"""ONE-TIME: wyczyść public schema przed pełnym baseline (usuń po udanym deployu).

Revision ID: reset_public_once
Revises:
Create Date: 2026-07-30
"""
from alembic import op
import sqlalchemy as sa

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
    op.execute("DROP TYPE IF EXISTS public.familyrole CASCADE")
    op.execute("DROP TYPE IF EXISTS public.notificationtype CASCADE")
    op.create_table(
        "alembic_version",
        sa.Column("version_num", sa.String(32), nullable=False, primary_key=True),
    )


def downgrade() -> None:
    pass
