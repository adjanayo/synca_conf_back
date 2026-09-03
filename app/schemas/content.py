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


class FaqCreate(BaseModel):
    category_id: int
    question: str
    answer: str
    sort_order: int = 0


class FaqUpdate(BaseModel):
    category_id: int | None = None
    question: str | None = None
    answer: str | None = None
    sort_order: int | None = None


class ContactMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    subject: str | None
    message: str
    is_read: bool
    created_at: datetime.datetime


class ContactMessageUpdate(BaseModel):
    is_read: bool
