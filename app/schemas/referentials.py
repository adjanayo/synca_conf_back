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


class PassContentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    label: str
    created_at: datetime.datetime


class PassContentCreate(BaseModel):
    label: str


class PassContentUpdate(BaseModel):
    label: str | None = None


class PassTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: int
    description: str | None
    max_days: int
    is_active: bool
    created_at: datetime.datetime
    contents: list[PassContentRead] = []


class PassTypeCreate(BaseModel):
    name: str
    price: int
    description: str | None = None
    max_days: int = 3
    is_active: bool = True
    content_ids: list[int] = []


class PassTypeUpdate(BaseModel):
    name: str | None = None
    price: int | None = None
    description: str | None = None
    max_days: int | None = None
    is_active: bool | None = None
    content_ids: list[int] | None = None


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


class PartnerLevelCreate(BaseModel):
    name: str
    price: int
    benefits: str | None = None
    sort_order: int = 0


class PartnerLevelUpdate(BaseModel):
    name: str | None = None
    price: int | None = None
    benefits: str | None = None
    sort_order: int | None = None


class FaqCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class FaqCategoryCreate(BaseModel):
    name: str


class FaqCategoryUpdate(BaseModel):
    name: str | None = None
