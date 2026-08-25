from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.referentials import PartnerLevel

APPLICATION_STATUS_VALUES = ("pending", "accepted", "rejected")
NEGOTIATION_STATUS_VALUES = ("pending", "contacted", "negotiating", "confirmed", "rejected")

INTERVENTION_FORMAT_VALUES = ("Keynote", "Panel", "Workshop", "Lightning Talk", "Fireside Chat")
THEME_VALUES = ("IA", "EdTech", "Entrepreneuriat", "Carrières", "Impact", "Cybersec")
AUDIENCE_LEVEL_VALUES = ("Débutant", "Intermédiaire", "Avancé", "Tous")
LANGUAGE_VALUES = ("Français", "Anglais", "Bilingue", "Autre")
AVAILABILITY_VALUES = ("Oui confirmé", "Sous réserve", "Besoin aide déplacement")
VIDEO_CONSENT_VALUES = ("Oui sans restriction", "Oui avec validation", "Non")

AMBASSADOR_PROFILE_VALUES = ("Étudiant", "Professionnel", "Créateur de contenu", "Entrepreneur")
FOLLOWERS_RANGE_VALUES = ("<500", "500-2K", "2K-10K", "+10K")
ESTIMATED_REACH_VALUES = ("5–10", "10–25", "25–50", "+50")
AVAILABILITY_PRE_VALUES = ("Oui", "Non", "Partielle")

PARTNER_SECTOR_VALUES = (
    "Tech/ESN",
    "Fintech",
    "Télécoms",
    "Banque",
    "ONG",
    "Université",
    "Médias",
    "Autre",
)
HAS_BUDGET_VALUES = ("Oui — budget précis", "Oui — à discuter", "Non — exploration")

STAND_TYPE_VALUES = ("Standard", "Premium", "Mutualisé")
EXHIBITOR_PAYMENT_METHOD_VALUES = (
    "Virement bancaire",
    "Mobile Money",
    "Chèque",
    "À définir avec l'équipe Synca",
)


class Speaker(Base):
    __tablename__ = "speakers"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    title_role: Mapped[str] = mapped_column(String(200), nullable=False)
    company: Mapped[str | None] = mapped_column(String(200))
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_whatsapp: Mapped[str] = mapped_column(String(20), nullable=False)
    linkedin_url: Mapped[str | None] = mapped_column(String(255))
    website_url: Mapped[str | None] = mapped_column(String(255))
    photo_url: Mapped[str | None] = mapped_column(String(255))
    intervention_format: Mapped[str] = mapped_column(
        Enum(*INTERVENTION_FORMAT_VALUES, name="speaker_intervention_format"), nullable=False
    )
    intervention_title: Mapped[str] = mapped_column(String(100), nullable=False)
    theme: Mapped[str] = mapped_column(Enum(*THEME_VALUES, name="speaker_theme"), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    audience_level: Mapped[str | None] = mapped_column(
        Enum(*AUDIENCE_LEVEL_VALUES, name="speaker_audience_level")
    )
    language: Mapped[str | None] = mapped_column(Enum(*LANGUAGE_VALUES, name="speaker_language"))
    past_experience: Mapped[str | None] = mapped_column(Text)
    video_link: Mapped[str | None] = mapped_column(String(255))
    availability: Mapped[str | None] = mapped_column(
        Enum(*AVAILABILITY_VALUES, name="speaker_availability")
    )
    departure_city: Mapped[str | None] = mapped_column(String(100))
    needs_accommodation: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    motivation: Mapped[str] = mapped_column(Text, nullable=False)
    video_consent: Mapped[str | None] = mapped_column(
        Enum(*VIDEO_CONSENT_VALUES, name="speaker_video_consent")
    )
    gdpr_consent: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0"
    )
    status: Mapped[str] = mapped_column(
        Enum(*APPLICATION_STATUS_VALUES, name="speaker_status"),
        default="pending",
        server_default="pending",
        index=True,
    )
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Ambassador(Base):
    __tablename__ = "ambassadors"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_whatsapp: Mapped[str] = mapped_column(String(20), nullable=False)
    current_profile: Mapped[str | None] = mapped_column(
        Enum(*AMBASSADOR_PROFILE_VALUES, name="ambassador_current_profile")
    )
    institution_company: Mapped[str | None] = mapped_column(String(200))
    linkedin_url: Mapped[str | None] = mapped_column(String(255))
    social_handles: Mapped[dict | None] = mapped_column(JSON)
    followers_range: Mapped[str | None] = mapped_column(
        Enum(*FOLLOWERS_RANGE_VALUES, name="ambassador_followers_range")
    )
    motivation: Mapped[str] = mapped_column(Text, nullable=False)
    mobilization_plan: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_reach: Mapped[str | None] = mapped_column(
        Enum(*ESTIMATED_REACH_VALUES, name="ambassador_estimated_reach")
    )
    previous_synca: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    preferred_channels: Mapped[str] = mapped_column(Text, nullable=False)
    availability_pre: Mapped[str | None] = mapped_column(
        Enum(*AVAILABILITY_PRE_VALUES, name="ambassador_availability_pre")
    )
    gdpr_consent: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0"
    )
    promo_code_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("promo_codes.id"))
    status: Mapped[str] = mapped_column(
        Enum(*APPLICATION_STATUS_VALUES, name="ambassador_status"),
        default="pending",
        server_default="pending",
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Partner(Base):
    __tablename__ = "partners"

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_name: Mapped[str] = mapped_column(String(200), nullable=False)
    sector: Mapped[str] = mapped_column(
        Enum(*PARTNER_SECTOR_VALUES, name="partner_sector"), nullable=False
    )
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    website_url: Mapped[str | None] = mapped_column(String(255))
    contact_name: Mapped[str] = mapped_column(String(200), nullable=False)
    contact_position: Mapped[str] = mapped_column(String(200), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    level_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("partner_levels.id"), nullable=False, index=True
    )
    has_budget: Mapped[str | None] = mapped_column(
        Enum(*HAS_BUDGET_VALUES, name="partner_has_budget")
    )
    objectives: Mapped[str] = mapped_column(Text, nullable=False)
    previous_sponsor: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    message: Mapped[str | None] = mapped_column(Text)
    heard_from: Mapped[str | None] = mapped_column(String(100))
    gdpr_consent: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0"
    )
    status: Mapped[str] = mapped_column(
        Enum(*NEGOTIATION_STATUS_VALUES, name="partner_status"),
        default="pending",
        server_default="pending",
        index=True,
    )
    logo_url: Mapped[str | None] = mapped_column(String(255))
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    level: Mapped[PartnerLevel] = relationship()


class Exhibitor(Base):
    __tablename__ = "exhibitors"

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_name: Mapped[str] = mapped_column(String(200), nullable=False)
    sector: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    website_url: Mapped[str | None] = mapped_column(String(255))
    contact_name: Mapped[str] = mapped_column(String(200), nullable=False)
    contact_position: Mapped[str] = mapped_column(String(200), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    stand_type: Mapped[str] = mapped_column(
        Enum(*STAND_TYPE_VALUES, name="exhibitor_stand_type"), nullable=False
    )
    reps_count: Mapped[int] = mapped_column(Integer, nullable=False)
    linked_partner_level: Mapped[str | None] = mapped_column(String(50))
    products_services: Mapped[str] = mapped_column(Text, nullable=False)
    equipment_needs: Mapped[str | None] = mapped_column(Text)
    side_activities: Mapped[str | None] = mapped_column(Text)
    visuals_url: Mapped[str | None] = mapped_column(String(255))
    payment_method: Mapped[str | None] = mapped_column(
        Enum(*EXHIBITOR_PAYMENT_METHOD_VALUES, name="exhibitor_payment_method")
    )
    rules_accepted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0"
    )
    gdpr_consent: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0"
    )
    status: Mapped[str] = mapped_column(
        Enum(*NEGOTIATION_STATUS_VALUES, name="exhibitor_status"),
        default="pending",
        server_default="pending",
        index=True,
    )
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
