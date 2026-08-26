from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.applications import (
    AUDIENCE_LEVEL_VALUES,
    AVAILABILITY_VALUES,
    INTERVENTION_FORMAT_VALUES,
    LANGUAGE_VALUES,
    THEME_VALUES,
    VIDEO_CONSENT_VALUES,
)


class SpeakerApplyCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    title_role: str = Field(min_length=1, max_length=200)
    company: str | None = Field(default=None, max_length=200)
    country: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone_whatsapp: str = Field(min_length=1, max_length=20)
    linkedin_url: str | None = None
    website_url: str | None = None
    intervention_format: Literal[*INTERVENTION_FORMAT_VALUES]
    intervention_title: str = Field(min_length=1, max_length=100)
    theme: Literal[*THEME_VALUES]
    summary: str = Field(min_length=1)
    audience_level: Literal[*AUDIENCE_LEVEL_VALUES] | None = None
    language: Literal[*LANGUAGE_VALUES] | None = None
    past_experience: str | None = None
    video_link: str | None = None
    availability: Literal[*AVAILABILITY_VALUES] | None = None
    departure_city: str | None = Field(default=None, max_length=100)
    needs_accommodation: bool = False
    motivation: str = Field(min_length=1)
    video_consent: Literal[*VIDEO_CONSENT_VALUES] | None = None
    gdpr_consent: bool

    @field_validator("gdpr_consent")
    @classmethod
    def gdpr_must_be_true(cls, value: bool) -> bool:
        if not value:
            raise ValueError("Le consentement RGPD est obligatoire.")
        return value
