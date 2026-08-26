from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.users import EXPERIENCE_LEVEL_VALUES, GENDER_VALUES, PROFILE_VALUES, SECTOR_VALUES


class RegisterCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    gender: Literal[*GENDER_VALUES] | None = None
    email: EmailStr
    phone_whatsapp: str = Field(min_length=1, max_length=20)
    country: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)
    profiles: list[Literal[*PROFILE_VALUES]] = Field(min_length=1)
    sector: Literal[*SECTOR_VALUES] | None = None
    experience_level: Literal[*EXPERIENCE_LEVEL_VALUES] | None = None
    pass_type_id: int
    promo_code: str | None = None
    linkedin_url: str | None = None
    portfolio_url: str | None = None
    special_needs: str | None = None
    heard_from: str | None = Field(default=None, max_length=100)
    gdpr_consent: bool
    newsletter_consent: bool = False

    @field_validator("gdpr_consent")
    @classmethod
    def gdpr_must_be_true(cls, value: bool) -> bool:
        if not value:
            raise ValueError("Le consentement RGPD est obligatoire.")
        return value
