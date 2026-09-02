import datetime

from pydantic import BaseModel, ConfigDict


class DayRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: datetime.date
    label: str
    created_at: datetime.datetime


class DayCreate(BaseModel):
    date: datetime.date
    label: str


class DayUpdate(BaseModel):
    date: datetime.date | None = None
    label: str | None = None


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


class PassTypeCreate(BaseModel):
    name: str
    price: int
    description: str | None = None
    inclusions: str | None = None
    max_days: int = 3
    is_active: bool = True


class PassTypeUpdate(BaseModel):
    name: str | None = None
    price: int | None = None
    description: str | None = None
    inclusions: str | None = None
    max_days: int | None = None
    is_active: bool | None = None


class EventSettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    venue: str
    year: int | None
    updated_at: datetime.datetime


class EventSettingsUpdate(BaseModel):
    name: str | None = None
    venue: str | None = None
    year: int | None = None


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
