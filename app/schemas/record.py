from __future__ import annotations

from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
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


class RecordFilter(BaseModel):
    type: Optional[RecordTypeEnum] = None
    category: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
