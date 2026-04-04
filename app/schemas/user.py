from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from enum import Enum


class RoleEnum(str, Enum):
    admin = "admin"
    analyst = "analyst"
    viewer = "viewer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: RoleEnum = RoleEnum.viewer

    @field_validator("password")
    @classmethod
    def password_min_length(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        return value


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateRole(BaseModel):
    role: RoleEnum


class UserUpdateStatus(BaseModel):
    is_active: bool
