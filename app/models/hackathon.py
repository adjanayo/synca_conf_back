from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class HackathonTeam(Base):
    __tablename__ = "hackathon_teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    university_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    project_name: Mapped[str] = mapped_column(String(200), nullable=False)
    project_description: Mapped[str] = mapped_column(Text, nullable=False)
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
    # Compte participant optionnel (table `users`) -- l'admin peut créer le
    # compte directement depuis le dashboard hackathon (pas besoin de passer
    # par l'inscription/billetterie publique) ou lier un participant déjà
    # inscrit. `full_name`/etc. restent saisis à part : un membre d'équipe
    # peut aussi n'être qu'une entrée texte, sans compte du tout. SET NULL
    # (pas CASCADE) -- supprimer le compte ne doit pas effacer la ligne du
    # roster, juste délier.
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    study_level: Mapped[str] = mapped_column(String(100), nullable=False)
    specialty: Mapped[str] = mapped_column(String(150), nullable=False)
    photo_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    team: Mapped[HackathonTeam] = relationship(back_populates="members")
