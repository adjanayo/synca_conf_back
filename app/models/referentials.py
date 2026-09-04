from datetime import date as date_type
from datetime import datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Day(Base):
    __tablename__ = "days"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date_type] = mapped_column(Date, unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class PassContent(Base):
    """Bénéfice/inclusion pilotable au dashboard -- catalogue global, coché
    par pass à la création plutôt que retapé en texte libre par pass
    (ROADMAP_PUBLIC_SEO.md Partie 8)."""

    __tablename__ = "pass_contents"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


pass_type_contents = Table(
    "pass_type_contents",
    Base.metadata,
    Column(
        "pass_type_id", Integer, ForeignKey("pass_types.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "pass_content_id",
        Integer,
        ForeignKey("pass_contents.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class PassType(Base):
    __tablename__ = "pass_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    max_days: Mapped[int] = mapped_column(Integer, default=3, server_default="3")
    is_active: Mapped[bool] = mapped_column(default=True, server_default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    contents: Mapped[list[PassContent]] = relationship(
        secondary=pass_type_contents, order_by=PassContent.id
    )


class PartnerBenefit(Base):
    """Avantage pilotable au dashboard -- catalogue global, coché par palier
    de partenariat à la création plutôt que retapé en texte libre par palier
    (même patron que PassContent, ROADMAP_PUBLIC_SEO.md Partie 8)."""

    __tablename__ = "partner_benefits"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


partner_level_benefits = Table(
    "partner_level_benefits",
    Base.metadata,
    Column(
        "partner_level_id",
        Integer,
        ForeignKey("partner_levels.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "partner_benefit_id",
        Integer,
        ForeignKey("partner_benefits.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class PartnerLevel(Base):
    __tablename__ = "partner_levels"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    benefits: Mapped[list[PartnerBenefit]] = relationship(
        secondary=partner_level_benefits, order_by=PartnerBenefit.id
    )


class FaqCategory(Base):
    __tablename__ = "faq_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)


class EventSettings(Base):
    __tablename__ = "event_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    venue: Mapped[str] = mapped_column(String(200), nullable=False)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
