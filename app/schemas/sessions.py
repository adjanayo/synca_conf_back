import datetime

from pydantic import BaseModel, ConfigDict


class SessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    day_id: int
    title: str
    description: str | None
    category: str
    start_time: datetime.time
    end_time: datetime.time
    room: str | None
    speaker_id: int | None
    is_public: bool
    created_at: datetime.datetime


class SessionCreate(BaseModel):
    day_id: int
    title: str
    description: str | None = None
    category: str
    start_time: datetime.time
    end_time: datetime.time
    room: str | None = None
    speaker_id: int | None = None
    is_public: bool = True


class SessionUpdate(BaseModel):
    day_id: int | None = None
    title: str | None = None
    description: str | None = None
    category: str | None = None
    start_time: datetime.time | None = None
    end_time: datetime.time | None = None
    room: str | None = None
    speaker_id: int | None = None
    is_public: bool | None = None
