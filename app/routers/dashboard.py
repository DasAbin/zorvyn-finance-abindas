from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.schemas.dashboard import SummaryResponse, CategoryTotal, DashboardTrends
from app.services.record_service import get_summary, get_category_totals, get_trends

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=SummaryResponse)
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get financial summary: total income, expenses, net balance, record count. All roles."""
    return get_summary(db)


@router.get("/categories", response_model=list[CategoryTotal])
def dashboard_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get category-wise totals. All roles."""
    return get_category_totals(db)


@router.get("/trends", response_model=DashboardTrends)
def dashboard_trends(
    period: str = Query("monthly", pattern="^(weekly|monthly)$", description="Trend period: weekly or monthly"),
    limit: int = Query(6, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get income/expense trends over the last 6 periods. All roles."""
    return DashboardTrends(trends=get_trends(db, period, limit))
