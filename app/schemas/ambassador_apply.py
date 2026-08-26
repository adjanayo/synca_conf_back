from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.applications import (
    AMBASSADOR_PROFILE_VALUES,
    AVAILABILITY_PRE_VALUES,
    ESTIMATED_REACH_VALUES,
    FOLLOWERS_RANGE_VALUES,
)


class AmbassadorApplyCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=16)
    country: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone_whatsapp: str = Field(min_length=1, max_length=20)
    current_profile: Literal[*AMBASSADOR_PROFILE_VALUES] | None = None
    institution_company: str | None = Field(default=None, max_length=200)
    linkedin_url: str | None = None
    social_handles: dict[str, str] | None = None
    followers_range: Literal[*FOLLOWERS_RANGE_VALUES] | None = None
    motivation: str = Field(min_length=1)
    mobilization_plan: str = Field(min_length=1)
    estimated_reach: Literal[*ESTIMATED_REACH_VALUES] | None = None
    previous_synca: bool = False
    preferred_channels: list[str] = Field(min_length=1)
    availability_pre: Literal[*AVAILABILITY_PRE_VALUES] | None = None
    gdpr_consent: bool

    @field_validator("gdpr_consent")
    @classmethod
    def gdpr_must_be_true(cls, value: bool) -> bool:
        if not value:
            raise ValueError("Le consentement RGPD est obligatoire.")
        return value
