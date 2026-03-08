import uuid
from datetime import date
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract
import io

from app.db.base import get_db
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction, TransactionType, TransactionCategory
from app.models.income import Income
from app.models.savings import SavingsGoal
from app.api.deps import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/dashboard")
async def dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Main dashboard summary."""
    from datetime import datetime

    today = date.today()

    # Total balance across all accounts
    acc_result = await db.execute(
        select(func.sum(Account.current_balance)).where(
            Account.owner_id == current_user.id, Account.is_active == True
        )
    )
    total_balance = acc_result.scalar() or Decimal("0")

    # Current month expenses
    exp_result = await db.execute(
        select(func.sum(Transaction.amount)).where(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == TransactionType.EXPENSE,
            extract("year", Transaction.transaction_date) == today.year,
            extract("month", Transaction.transaction_date) == today.month,
        )
    )
    month_expenses = exp_result.scalar() or Decimal("0")

    # Current month income
    inc_result = await db.execute(
        select(func.sum(Income.amount)).where(
            Income.user_id == current_user.id,
            Income.is_skipped == False,
            extract("year", Income.income_date) == today.year,
            extract("month", Income.income_date) == today.month,
        )
    )
    month_income = inc_result.scalar() or Decimal("0")

    # Total savings
    sav_result = await db.execute(
        select(func.sum(SavingsGoal.current_amount)).where(
            SavingsGoal.user_id == current_user.id,
            SavingsGoal.is_active == True,
        )
    )
    total_savings = sav_result.scalar() or Decimal("0")

    return {
        "total_balance": str(total_balance),
        "month_expenses": str(month_expenses),
        "month_income": str(month_income),
        "total_savings": str(total_savings),
        "cashflow": str(month_income - month_expenses),
    }


@router.get("/expenses-by-category")
async def expenses_by_category(
    year: int = Query(default=date.today().year),
    month: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conditions = [
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == TransactionType.EXPENSE,
        extract("year", Transaction.transaction_date) == year,
    ]
    if month:
        conditions.append(extract("month", Transaction.transaction_date) == month)

    result = await db.execute(
        select(
            TransactionCategory.name,
            func.sum(Transaction.amount).label("total"),
        )
        .join(TransactionCategory, Transaction.category_id == TransactionCategory.id, isouter=True)
        .where(and_(*conditions))
        .group_by(TransactionCategory.name)
        .order_by(func.sum(Transaction.amount).desc())
    )
    rows = result.all()
    return [{"category": r[0] or "Bez kategorii", "amount": str(r[1])} for r in rows]


@router.get("/monthly-trend")
async def monthly_trend(
    months: int = Query(default=12, ge=1, le=24),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Expenses and income trend over last N months."""
    from datetime import datetime, timedelta

    today = date.today()
    results = []

    for i in range(months - 1, -1, -1):
        # Calculate year/month
        month_num = today.month - i
        year = today.year
        while month_num <= 0:
            month_num += 12
            year -= 1

        exp_result = await db.execute(
            select(func.sum(Transaction.amount)).where(
                Transaction.user_id == current_user.id,
                Transaction.transaction_type == TransactionType.EXPENSE,
                extract("year", Transaction.transaction_date) == year,
                extract("month", Transaction.transaction_date) == month_num,
            )
        )
        expenses = exp_result.scalar() or Decimal("0")

        inc_result = await db.execute(
            select(func.sum(Income.amount)).where(
                Income.user_id == current_user.id,
                Income.is_skipped == False,
                extract("year", Income.income_date) == year,
                extract("month", Income.income_date) == month_num,
            )
        )
        income = inc_result.scalar() or Decimal("0")

        results.append({
            "year": year,
            "month": month_num,
            "label": f"{year}-{month_num:02d}",
            "expenses": str(expenses),
            "income": str(income),
            "cashflow": str(income - expenses),
        })

    return results


@router.get("/export/transactions")
async def export_transactions(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export transactions to Excel (.xlsx)."""
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter

    conditions = [Transaction.user_id == current_user.id]
    if start_date:
        conditions.append(Transaction.transaction_date >= start_date)
    if end_date:
        conditions.append(Transaction.transaction_date <= end_date)

    result = await db.execute(
        select(Transaction).where(and_(*conditions))
        .order_by(Transaction.transaction_date.desc())
    )
    transactions = result.scalars().all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Transakcje"

    headers = ["Data", "Typ", "Kwota", "Waluta", "Kwota PLN", "Opis", "Zakres"]
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)

    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    for row, tx in enumerate(transactions, 2):
        ws.cell(row=row, column=1, value=str(tx.transaction_date))
        ws.cell(row=row, column=2, value=tx.transaction_type.value)
        ws.cell(row=row, column=3, value=float(tx.amount))
        ws.cell(row=row, column=4, value=tx.currency)
        ws.cell(row=row, column=5, value=float(tx.amount_pln) if tx.amount_pln else None)
        ws.cell(row=row, column=6, value=tx.description or "")
        ws.cell(row=row, column=7, value=tx.scope.value)

    # Auto-fit columns
    for col in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 15

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=transakcje.xlsx"},
    )
