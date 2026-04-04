from __future__ import annotations

from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional, List
from enum import Enum


class RecordTypeEnum(str, Enum):
    income = "income"
    expense = "expense"


class RecordCreate(BaseModel):
    amount: float
    type: RecordTypeEnum
    category: str
    date: date
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("Amount must be greater than zero")
        return value


class RecordUpdate(BaseModel):
    amount: Optional[float] = None
    type: Optional[RecordTypeEnum] = None
    category: Optional[str] = None
    date: Optional[date] = None
    notes: Optional[str] = None


class RecordResponse(BaseModel):
    id: int
    amount: float
    type: str
    category: str
    date: date
    notes: Optional[str]
    is_deleted: bool
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedRecords(BaseModel):
    data: List[RecordResponse]
    total: int
    page: int
    limit: int


class RecordFilter(BaseModel):
    type: Optional[RecordTypeEnum] = None
    category: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
