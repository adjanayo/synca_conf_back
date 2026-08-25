import datetime

from pydantic import BaseModel, ConfigDict


class DayRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: datetime.date
    label: str
    created_at: datetime.datetime


class PassTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: int
    description: str | None
    inclusions: str | None
    max_days: int
    is_active: bool
    created_at: datetime.datetime


class PartnerLevelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: int
    benefits: str | None
    sort_order: int
    created_at: datetime.datetime


class FaqCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
