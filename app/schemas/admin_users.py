from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr

AdminUserStatus = Literal["active", "disabled", "archived"]


class AdminUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role_id: int
    role_name: str
    status: AdminUserStatus
    last_login: datetime | None
    created_at: datetime


class AdminUserCreate(BaseModel):
    email: EmailStr
    password: str
    role_id: int


class AdminUserUpdate(BaseModel):
    email: EmailStr | None = None
    role_id: int | None = None
    status: AdminUserStatus | None = None
    password: str | None = None
