from pydantic import BaseModel
from decimal import Decimal

class SummaryResponse(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    net_balance: Decimal
    record_count: int


class CategoryTotal(BaseModel):
    category: str
    total: Decimal


class TrendPoint(BaseModel):
    period: str
    income: Decimal
    expense: Decimal


class DashboardTrends(BaseModel):
    trends: list[TrendPoint]
