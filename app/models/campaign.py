from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

CAMPAIGN_WINDOW_KEY_VALUES = (
    "call_for_speaker",
    "ticketing",
    "call_for_partner",
    "call_for_ambassador",
    "call_for_exhibitor",
    "event",
    "hackathon_universitaire",
    "call_for_community_certified",
)


class CampaignWindow(Base):
    __tablename__ = "campaign_windows"
    __table_args__ = (CheckConstraint("end_at > start_at", name="ck_campaign_window_dates"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(
        Enum(*CAMPAIGN_WINDOW_KEY_VALUES, name="campaign_window_key"), unique=True, nullable=False
    )
    start_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
