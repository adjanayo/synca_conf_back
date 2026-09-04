from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class HackathonTeam(Base):
    __tablename__ = "hackathon_teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    university_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    project_name: Mapped[str] = mapped_column(String(200), nullable=False)
    project_description: Mapped[str] = mapped_column(Text, nullable=False)
    # Masquer/afficher une équipe sans la supprimer -- même patron que
    # Speaker/Session/Ambassador/Partner/Exhibitor.is_public.
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    members: Mapped[list["HackathonTeamMember"]] = relationship(
        back_populates="team", order_by="HackathonTeamMember.id"
    )


class HackathonTeamMember(Base):
    __tablename__ = "hackathon_team_members"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("hackathon_teams.id"), nullable=False, index=True
    )
    # Les membres du hackathon ne sont volontairement PAS liés à la table
    # `users` (inscrits/billetterie) -- demande explicite de l'utilisateur,
    # ce sont deux populations distinctes. Toutes les infos sont saisies à
    # la main au dashboard.
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    study_level: Mapped[str] = mapped_column(String(100), nullable=False)
    specialty: Mapped[str] = mapped_column(String(150), nullable=False)
    photo_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    team: Mapped[HackathonTeam] = relationship(back_populates="members")
