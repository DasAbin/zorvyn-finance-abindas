from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserResponse, UserUpdateRole, UserUpdateStatus
from app.services.user_service import get_all_users, update_role, update_status
from app.dependencies.rbac import require_role
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from fastapi import HTTPException, status

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_active_user)):
    """Get currently authenticated user's profile. All roles."""
    return current_user


@router.get("/", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """List all users. Admin only."""
    return get_all_users(db)


@router.patch("/{user_id}/role", response_model=UserResponse)
def change_user_role(
    user_id: int,
    data: UserUpdateRole,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Update a user's role. Admin only."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot modify your own role or status")
    return update_role(db, user_id, data.role.value)


@router.patch("/{user_id}/status", response_model=UserResponse)
def change_user_status(
    user_id: int,
    data: UserUpdateStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Toggle a user's active status. Admin only."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot modify your own role or status")
    return update_status(db, user_id, data.is_active)
