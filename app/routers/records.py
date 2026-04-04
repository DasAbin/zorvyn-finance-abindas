from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import date, datetime, timezone
from typing import Optional
from app.core.database import get_db
from app.models.record import FinancialRecord
from app.models.user import User
from app.schemas.record import RecordCreate, RecordUpdate, RecordResponse, PaginatedRecords
from app.dependencies.rbac import require_role
from app.dependencies.auth import get_current_active_user
from app.services.record_service import get_records

router = APIRouter(prefix="/records", tags=["Financial Records"])


@router.post("/", response_model=RecordResponse, status_code=status.HTTP_201_CREATED)
def create_record(
    data: RecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "analyst")),
):
    """Create a new financial record. Admin and Analyst only."""
    record = FinancialRecord(
        amount=data.amount,
        type=data.type.value,
        category=data.category,
        date=data.date,
        notes=data.notes,
        created_by=current_user.id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/", response_model=PaginatedRecords)
def list_records(
    type: Optional[str] = Query(None, description="Filter by type: income or expense"),
    category: Optional[str] = Query(None, description="Filter by category"),
    date_from: Optional[date] = Query(None, description="Start date filter"),
    date_to: Optional[date] = Query(None, description="End date filter"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Records per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List financial records with filtering and pagination. All roles."""
    records, total = get_records(
        db, record_type=type, category=category,
        date_from=date_from, date_to=date_to,
        page=page, limit=limit,
    )
    return {"data": records, "total": total, "page": page, "limit": limit}


@router.get("/{record_id}", response_model=RecordResponse)
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a single financial record by ID. All roles."""
    record = db.query(FinancialRecord).filter(
        FinancialRecord.id == record_id,
        FinancialRecord.is_deleted == False,
    ).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record


@router.patch("/{record_id}", response_model=RecordResponse)
def update_record(
    record_id: int,
    data: RecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "analyst")),
):
    """Partially update a financial record. Admin and Analyst only."""
    record = db.query(FinancialRecord).filter(
        FinancialRecord.id == record_id,
        FinancialRecord.is_deleted == False,
    ).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    update_data = data.model_dump(exclude_unset=True)
    if "type" in update_data and update_data["type"] is not None:
        update_data["type"] = update_data["type"].value

    for field, value in update_data.items():
        setattr(record, field, value)

    record.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", status_code=status.HTTP_200_OK)
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Soft-delete a financial record. Admin only."""
    record = db.query(FinancialRecord).filter(
        FinancialRecord.id == record_id,
        FinancialRecord.is_deleted == False,
    ).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    record.is_deleted = True
    record.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"detail": "Record soft-deleted successfully"}
