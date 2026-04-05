from sqlalchemy import Column, Integer, Numeric, String, Boolean, Date, DateTime, ForeignKey
from datetime import datetime, timezone
from app.core.database import Base


class FinancialRecord(Base):
    __tablename__ = "financial_records"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(precision=15, scale=2), nullable=False)
    type = Column(String, nullable=False)  # income, expense
    category = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    notes = Column(String, nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
