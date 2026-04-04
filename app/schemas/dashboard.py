from pydantic import BaseModel


class SummaryResponse(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    record_count: int


class CategoryTotal(BaseModel):
    category: str
    total: float


class TrendPoint(BaseModel):
    period: str
    income: float
    expense: float


class DashboardTrends(BaseModel):
    trends: list[TrendPoint]
