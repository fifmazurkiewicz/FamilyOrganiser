"""Add shopping, tasks, simple expenses, monthly budgets, and simple investments

Revision ID: add_family_organiser_modules
Revises: add_recurring_freq
Create Date: 2026-07-26

Usage: cd backend && alembic upgrade head
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "add_family_organiser_modules"
down_revision = "add_recurring_freq"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── shopping_lists ───────────────────────────────────────────
    op.create_table(
        "shopping_lists",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("family_group_id", UUID(as_uuid=True),
                  sa.ForeignKey("family_groups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("created_by", UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── shopping_items ───────────────────────────────────────────
    op.create_table(
        "shopping_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("list_id", UUID(as_uuid=True),
                  sa.ForeignKey("shopping_lists.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("added_by", UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("bought_by", UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("bought_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_bought", sa.Boolean(), nullable=False, server_default="false"),
    )

    # ── task_lists ────────────────────────────────────────────────
    op.create_table(
        "task_lists",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("family_group_id", UUID(as_uuid=True),
                  sa.ForeignKey("family_groups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("created_by", UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── task_items ────────────────────────────────────────────────
    op.create_table(
        "task_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("list_id", UUID(as_uuid=True),
                  sa.ForeignKey("task_lists.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("assigned_to", UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("done_by", UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("done_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_done", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("due_date", sa.Date(), nullable=True),
    )

    # ── simple_expenses ───────────────────────────────────────────
    op.create_table(
        "simple_expenses",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("family_group_id", UUID(as_uuid=True),
                  sa.ForeignKey("family_groups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── monthly_budgets ───────────────────────────────────────────
    op.create_table(
        "monthly_budgets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("family_group_id", UUID(as_uuid=True),
                  sa.ForeignKey("family_groups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── monthly_budget_entries ────────────────────────────────────
    op.create_table(
        "monthly_budget_entries",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("budget_id", UUID(as_uuid=True),
                  sa.ForeignKey("monthly_budgets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entry_type", sa.String(10), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_by", UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    )

    # ── simple_investments ────────────────────────────────────────
    op.create_table(
        "simple_investments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("family_group_id", UUID(as_uuid=True),
                  sa.ForeignKey("family_groups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("investment_type", sa.String(20), nullable=False),
        sa.Column("principal_amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("interest_rate", sa.Numeric(6, 4), nullable=False),
        sa.Column("interest_period", sa.String(20), nullable=False, server_default="yearly"),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("duration_value", sa.Integer(), nullable=False),
        sa.Column("duration_unit", sa.String(20), nullable=False, server_default="months"),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("projected_profit", sa.Numeric(15, 2), nullable=True),
        sa.Column("projected_total", sa.Numeric(15, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("simple_investments")
    op.drop_table("monthly_budget_entries")
    op.drop_table("monthly_budgets")
    op.drop_table("simple_expenses")
    op.drop_table("task_items")
    op.drop_table("task_lists")
    op.drop_table("shopping_items")
    op.drop_table("shopping_lists")