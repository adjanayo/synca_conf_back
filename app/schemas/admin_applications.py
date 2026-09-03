from typing import Literal

from pydantic import BaseModel, EmailStr, Field

from app.models.applications import (
    AMBASSADOR_PROFILE_VALUES,
    APPLICATION_STATUS_VALUES,
    AUDIENCE_LEVEL_VALUES,
    AVAILABILITY_PRE_VALUES,
    AVAILABILITY_VALUES,
    ESTIMATED_REACH_VALUES,
    EXHIBITOR_PAYMENT_METHOD_VALUES,
    FOLLOWERS_RANGE_VALUES,
    HAS_BUDGET_VALUES,
    INTERVENTION_FORMAT_VALUES,
    LANGUAGE_VALUES,
    NEGOTIATION_STATUS_VALUES,
    PARTNER_SECTOR_VALUES,
    STAND_TYPE_VALUES,
    THEME_VALUES,
    VIDEO_CONSENT_VALUES,
)


class SpeakerStatusUpdate(BaseModel):
    status: Literal[*APPLICATION_STATUS_VALUES]


class AmbassadorStatusUpdate(BaseModel):
    status: Literal[*APPLICATION_STATUS_VALUES]


class PartnerStatusUpdate(BaseModel):
    status: Literal[*NEGOTIATION_STATUS_VALUES]


class ExhibitorStatusUpdate(BaseModel):
    status: Literal[*NEGOTIATION_STATUS_VALUES]


# --- Admin direct-create schemas (Phase K) -------------------------------
# Unlike the public *ApplyCreate schemas, these have no gdpr_consent /
# rules_accepted "must be true" validator -- an admin entering a record on
# behalf of an applicant (e.g. from a paper form, an email, a phone call)
# should not be blocked by a consent checkbox the applicant already gave
# out-of-band. gdpr_consent / rules_accepted default to False and are
# accepted as-is.


class SpeakerAdminCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    title_role: str = Field(min_length=1, max_length=200)
    company: str | None = Field(default=None, max_length=200)
    country: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone_whatsapp: str = Field(min_length=1, max_length=20)
    linkedin_url: str | None = None
    website_url: str | None = None
    photo_url: str | None = None
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
    gdpr_consent: bool = False
    status: Literal[*APPLICATION_STATUS_VALUES] = "accepted"
    is_public: bool = False


class AmbassadorAdminCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=16)
    country: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone_whatsapp: str = Field(min_length=1, max_length=20)
    photo_url: str | None = None
    current_profile: Literal[*AMBASSADOR_PROFILE_VALUES] | None = None
    institution_company: str | None = Field(default=None, max_length=200)
    linkedin_url: str | None = None
    social_handles: dict[str, str] | None = None
    followers_range: Literal[*FOLLOWERS_RANGE_VALUES] | None = None
    motivation: str = Field(min_length=1)
    mobilization_plan: str = Field(min_length=1)
    estimated_reach: Literal[*ESTIMATED_REACH_VALUES] | None = None
    previous_synca: bool = False
    # Free text (matches the `preferred_channels TEXT` column directly) --
    # unlike the public form's list[str], which the /apply route itself
    # joins with ", " before persisting.
    preferred_channels: str = Field(min_length=1)
    availability_pre: Literal[*AVAILABILITY_PRE_VALUES] | None = None
    gdpr_consent: bool = False
    status: Literal[*APPLICATION_STATUS_VALUES] = "accepted"


class PartnerAdminCreate(BaseModel):
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
    # Free text (matches the `objectives TEXT` column directly) -- see
    # preferred_channels note above.
    objectives: str = Field(min_length=1)
    previous_sponsor: bool = False
    message: str | None = None
    heard_from: str | None = Field(default=None, max_length=100)
    gdpr_consent: bool = False
    # NB: Partner.status is a NEGOTIATION_STATUS_VALUES enum
    # (pending/contacted/negotiating/confirmed/rejected) -- there is no
    # "accepted" value here, so the fully-approved default is "confirmed"
    # (the same status the existing PATCH route flips is_public on).
    status: Literal[*NEGOTIATION_STATUS_VALUES] = "confirmed"
    logo_url: str | None = None
    is_public: bool = False


class ExhibitorAdminCreate(BaseModel):
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
    # Free text (matches the `equipment_needs` / `side_activities` TEXT
    # columns directly) -- see preferred_channels note above.
    equipment_needs: str | None = None
    side_activities: str | None = None
    visuals_url: str | None = None
    payment_method: Literal[*EXHIBITOR_PAYMENT_METHOD_VALUES] | None = None
    rules_accepted: bool = False
    gdpr_consent: bool = False
    # See PartnerAdminCreate.status note -- Exhibitor.status is also a
    # NEGOTIATION_STATUS_VALUES enum, no "accepted" value.
    status: Literal[*NEGOTIATION_STATUS_VALUES] = "confirmed"
    is_public: bool = False
