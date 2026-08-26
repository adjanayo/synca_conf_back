from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.applications import HAS_BUDGET_VALUES, PARTNER_SECTOR_VALUES


class PartnerApplyCreate(BaseModel):
    organization_name: str = Field(min_length=1, max_length=200)
    sector: Literal[*PARTNER_SECTOR_VALUES]
    country: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)
    website_url: str | None = None
    contact_name: str = Field(min_length=1, max_length=200)
    contact_position: str = Field(min_length=1, max_length=200)
    contact_email: EmailStr
    contact_phone: str = Field(min_length=1, max_length=20)
    level_id: int
    has_budget: Literal[*HAS_BUDGET_VALUES] | None = None
    objectives: list[str] = Field(min_length=1)
    previous_sponsor: bool = False
    message: str | None = None
    heard_from: str | None = Field(default=None, max_length=100)
    gdpr_consent: bool

    @field_validator("gdpr_consent")
    @classmethod
    def gdpr_must_be_true(cls, value: bool) -> bool:
        if not value:
            raise ValueError("Le consentement RGPD est obligatoire.")
        return value
