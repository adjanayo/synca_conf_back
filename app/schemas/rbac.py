import datetime

from pydantic import BaseModel, ConfigDict


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class RoleUpdate(BaseModel):
    permission_codes: list[str]


class RoleWithPermissionsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    permission_codes: list[str]


class PermissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str


class RolePermissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role_id: int
    permission_id: int


class AdminUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role_id: int
    last_login: datetime.datetime | None
    created_at: datetime.datetime
