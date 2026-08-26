import datetime

from pydantic import BaseModel, ConfigDict


class UserProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    profile: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    gender: str | None
    email: str
    email_verified: bool
    phone_whatsapp: str
    country: str
    city: str
    sector: str | None
    experience_level: str | None
    linkedin_url: str | None
    portfolio_url: str | None
    special_needs: str | None
    heard_from: str | None
    gdpr_consent: bool
    newsletter_consent: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime


class RegisterResponse(UserRead):
    # Only ever returned once, at registration -- the participant's bearer
    # credential for GET/DELETE /api/user/me (6.8). There's no login for
    # participants and no "forgot my token" recovery, so this is the one
    # moment it's shown.
    access_token: str
