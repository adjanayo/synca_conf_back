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
