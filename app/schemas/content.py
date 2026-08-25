import datetime

from pydantic import BaseModel, ConfigDict


class FaqRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    question: str
    answer: str
    sort_order: int
    created_at: datetime.datetime


class ContactMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    subject: str | None
    message: str
    is_read: bool
    created_at: datetime.datetime
