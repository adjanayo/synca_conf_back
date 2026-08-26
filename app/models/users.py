from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

GENDER_VALUES = ("Homme", "Femme", "Autre")
SECTOR_VALUES = ("Dev", "Data", "Design", "Cybersec", "Product", "IA", "Autre")
EXPERIENCE_LEVEL_VALUES = ("Débutant", "Junior", "Senior", "Expert")
PROFILE_VALUES = ("Étudiant", "Professionnel", "Entrepreneur", "Recruteur", "Autre")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[str | None] = mapped_column(Enum(*GENDER_VALUES, name="user_gender"))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    # RGPD self-service (6.8): bearer credential for GET/DELETE /api/user/me.
    # No login exists for participants, so this is generated once at
    # registration (secrets.token_urlsafe) and given to the user then --
    # never re-issued through a "forgot my token" flow, same anti-enumeration
    # posture as security-hardening's customer-access-code guidance.
    access_token: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    phone_whatsapp: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    sector: Mapped[str | None] = mapped_column(Enum(*SECTOR_VALUES, name="user_sector"))
    experience_level: Mapped[str | None] = mapped_column(
        Enum(*EXPERIENCE_LEVEL_VALUES, name="user_experience_level")
    )
    linkedin_url: Mapped[str | None] = mapped_column(String(255))
    portfolio_url: Mapped[str | None] = mapped_column(String(255))
    special_needs: Mapped[str | None] = mapped_column(Text)
    heard_from: Mapped[str | None] = mapped_column(String(100))
    gdpr_consent: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0"
    )
    newsletter_consent: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    profiles: Mapped[list["UserProfile"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"
    __table_args__ = (UniqueConstraint("user_id", "profile", name="uq_user_profile"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    profile: Mapped[str] = mapped_column(
        Enum(*PROFILE_VALUES, name="user_profile_value"), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="profiles")
