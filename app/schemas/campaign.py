import datetime

from pydantic import BaseModel, ConfigDict


class CampaignWindowRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    key: str
    start_at: datetime.datetime
    end_at: datetime.datetime
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime


class CampaignWindowUpdate(BaseModel):
    start_at: datetime.datetime | None = None
    end_at: datetime.datetime | None = None
    is_active: bool | None = None
