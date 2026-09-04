from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ParticipantRead(BaseModel):
    """Sous-ensemble minimal de `User` pour la recherche/liaison admin (ex.
    membres d'équipe hackathon) -- pas de PII sensible (téléphone, etc.)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: str


class ParticipantCreate(BaseModel):
    """Création directe d'un compte participant par un admin (pas via
    l'inscription/billetterie publique) -- ex. étudiants du hackathon
    universitaire qui n'achètent pas de pass. Consentement RGPD attesté par
    l'admin à la création (même registre que la création directe de
    candidatures speaker/ambassadeur/partenaire/exposant)."""

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone_whatsapp: str = Field(min_length=1, max_length=20)
    country: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)
