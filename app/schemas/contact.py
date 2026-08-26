from pydantic import BaseModel, EmailStr, Field


class ContactCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    subject: str | None = Field(default=None, max_length=255)
    message: str = Field(min_length=1)
    captcha: str
