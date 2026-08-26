import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class NewsletterCreate(BaseModel):
    email: EmailStr


class NewsletterSubscriberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    created_at: datetime.datetime
