from pydantic import BaseModel, EmailStr


class WaitlistCreate(BaseModel):
    email: EmailStr
