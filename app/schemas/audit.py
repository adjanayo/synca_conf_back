import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event: str
    email: str
    ip_address: str | None
    success: bool
    created_at: datetime.datetime
