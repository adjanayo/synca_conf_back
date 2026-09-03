import datetime

from pydantic import BaseModel, ConfigDict


class SpeakerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    title_role: str
    company: str | None
    country: str
    email: str
    phone_whatsapp: str
    linkedin_url: str | None
    website_url: str | None
    photo_url: str | None
    intervention_format: str
    intervention_title: str
    theme: str
    summary: str
    audience_level: str | None
    language: str | None
    past_experience: str | None
    video_link: str | None
    availability: str | None
    departure_city: str | None
    needs_accommodation: bool
    motivation: str
    video_consent: str | None
    gdpr_consent: bool
    status: str
    is_public: bool
    created_at: datetime.datetime


class AmbassadorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    age: int
    country: str
    city: str
    email: str
    phone_whatsapp: str
    photo_url: str | None
    current_profile: str | None
    institution_company: str | None
    linkedin_url: str | None
    social_handles: dict | None
    followers_range: str | None
    motivation: str
    mobilization_plan: str
    estimated_reach: str | None
    previous_synca: bool
    preferred_channels: str
    availability_pre: str | None
    gdpr_consent: bool
    promo_code_id: int | None
    status: str
    is_public: bool
    created_at: datetime.datetime


class SpeakerPublicRead(BaseModel):
    """Sous-ensemble sans PII de SpeakerRead, pour les endpoints publics (liste + détail)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    title_role: str
    company: str | None
    country: str
    linkedin_url: str | None
    website_url: str | None
    photo_url: str | None
    intervention_format: str
    intervention_title: str
    theme: str
    summary: str
    audience_level: str | None
    language: str | None


class AmbassadorPublicRead(BaseModel):
    """Sous-ensemble sans PII de AmbassadorRead, pour les endpoints publics (liste + détail)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    country: str
    city: str
    photo_url: str | None
    current_profile: str | None
    institution_company: str | None
    linkedin_url: str | None
    social_handles: dict | None


class PartnerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_name: str
    sector: str
    country: str
    city: str
    website_url: str | None
    contact_name: str
    contact_position: str
    contact_email: str
    contact_phone: str
    level_id: int
    has_budget: str | None
    objectives: str
    previous_sponsor: bool
    message: str | None
    heard_from: str | None
    gdpr_consent: bool
    status: str
    logo_url: str | None
    is_public: bool
    created_at: datetime.datetime


class ExhibitorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_name: str
    sector: str
    country: str
    city: str
    website_url: str | None
    contact_name: str
    contact_position: str
    contact_email: str
    contact_phone: str
    stand_type: str
    reps_count: int
    linked_partner_level: str | None
    products_services: str
    equipment_needs: str | None
    side_activities: str | None
    visuals_url: str | None
    payment_method: str | None
    rules_accepted: bool
    gdpr_consent: bool
    status: str
    is_public: bool
    created_at: datetime.datetime


class PartnerPublicRead(BaseModel):
    """Sous-ensemble sans PII de PartnerRead, pour l'endpoint public /api/partners."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_name: str
    website_url: str | None
    logo_url: str | None
    level_id: int


class ExhibitorPublicRead(BaseModel):
    """Sous-ensemble sans PII de ExhibitorRead, pour l'endpoint public /api/exhibitors."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_name: str
    website_url: str | None
    stand_type: str
