from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.applications import EXHIBITOR_PAYMENT_METHOD_VALUES, STAND_TYPE_VALUES


class ExhibitorApplyCreate(BaseModel):
    organization_name: str = Field(min_length=1, max_length=200)
    sector: str = Field(min_length=1, max_length=100)
    country: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)
    website_url: str | None = None
    contact_name: str = Field(min_length=1, max_length=200)
    contact_position: str = Field(min_length=1, max_length=200)
    contact_email: EmailStr
    contact_phone: str = Field(min_length=1, max_length=20)
    stand_type: Literal[*STAND_TYPE_VALUES]
    reps_count: int = Field(ge=1)
    linked_partner_level: str | None = Field(default=None, max_length=50)
    products_services: str = Field(min_length=1)
    equipment_needs: list[str] | None = None
    side_activities: list[str] | None = None
    visuals_url: str | None = None
    payment_method: Literal[*EXHIBITOR_PAYMENT_METHOD_VALUES] | None = None
    rules_accepted: bool
    gdpr_consent: bool

    @field_validator("rules_accepted")
    @classmethod
    def rules_must_be_accepted(cls, value: bool) -> bool:
        if not value:
            raise ValueError("Le règlement de l'espace exposition doit être accepté.")
        return value

    @field_validator("gdpr_consent")
    @classmethod
    def gdpr_must_be_true(cls, value: bool) -> bool:
        if not value:
            raise ValueError("Le consentement RGPD est obligatoire.")
        return value
