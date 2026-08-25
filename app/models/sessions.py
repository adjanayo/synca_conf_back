from datetime import datetime, time

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.referentials import Day

SESSION_CATEGORY_VALUES = (
    "panel",
    "workshop",
    "competition",
    "keynote",
    "lightning_talk",
    "fireside_chat",
    "b2b",
    "job_fair",
    "networking",
    "after_party",
)


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    day_id: Mapped[int] = mapped_column(Integer, ForeignKey("days.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str] = mapped_column(
        Enum(*SESSION_CATEGORY_VALUES, name="session_category"), nullable=False, index=True
    )
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    room: Mapped[str | None] = mapped_column(String(100))
    # FK vers speakers.id ajoutée en 1.5 (la table speakers n'existe pas encore ici),
    # cf. schema.md §1 (ALTER TABLE sessions ADD CONSTRAINT fk_speaker ...).
    speaker_id: Mapped[int | None] = mapped_column(Integer)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    day: Mapped[Day] = relationship()
