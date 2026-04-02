from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from typing import Optional
from app.models.record import FinancialRecord
from app.schemas.dashboard import SummaryResponse, CategoryTotal, TrendPoint


def get_records(
    db: Session,
    record_type: Optional[str] = None,
    category: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[FinancialRecord], int]:
    query = db.query(FinancialRecord).filter(FinancialRecord.is_deleted == False)

    if record_type:
        query = query.filter(FinancialRecord.type == record_type)
    if category:
        query = query.filter(FinancialRecord.category == category)
    if date_from:
        query = query.filter(FinancialRecord.date >= date_from)
    if date_to:
        query = query.filter(FinancialRecord.date <= date_to)

    total = query.count()
    records = query.order_by(FinancialRecord.date.desc()).offset((page - 1) * limit).limit(limit).all()
    return records, total


def get_summary(db: Session) -> SummaryResponse:
    base = db.query(FinancialRecord).filter(FinancialRecord.is_deleted == False)

    total_income = (
        base.filter(FinancialRecord.type == "income")
        .with_entities(func.coalesce(func.sum(FinancialRecord.amount), 0))
        .scalar()
    )
    total_expenses = (
        base.filter(FinancialRecord.type == "expense")
        .with_entities(func.coalesce(func.sum(FinancialRecord.amount), 0))
        .scalar()
    )
    record_count = base.count()

    return SummaryResponse(
        total_income=float(total_income),
        total_expenses=float(total_expenses),
        net_balance=float(total_income) - float(total_expenses),
        record_count=record_count,
    )


def get_category_totals(db: Session) -> list[CategoryTotal]:
    results = (
        db.query(
            FinancialRecord.category,
            func.sum(FinancialRecord.amount).label("total"),
        )
        .filter(FinancialRecord.is_deleted == False)
        .group_by(FinancialRecord.category)
        .all()
    )
    return [CategoryTotal(category=r.category, total=float(r.total)) for r in results]


def get_trends(db: Session, period: str = "monthly") -> list[TrendPoint]:
    if period == "weekly":
        period_expr = func.strftime("%Y-%W", FinancialRecord.date)
    else:
        period_expr = func.strftime("%Y-%m", FinancialRecord.date)

    results = (
        db.query(
            period_expr.label("period"),
            func.sum(
                func.case(
                    (FinancialRecord.type == "income", FinancialRecord.amount),
                    else_=0,
                )
            ).label("income"),
            func.sum(
                func.case(
                    (FinancialRecord.type == "expense", FinancialRecord.amount),
                    else_=0,
                )
            ).label("expense"),
        )
        .filter(FinancialRecord.is_deleted == False)
        .group_by("period")
        .order_by(period_expr.desc())
        .limit(6)
        .all()
    )

    trends = [
        TrendPoint(period=r.period, income=float(r.income), expense=float(r.expense))
        for r in results
    ]
    trends.reverse()
    return trends
