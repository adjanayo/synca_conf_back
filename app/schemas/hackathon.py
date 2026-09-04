from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HackathonTeamMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    team_id: int
    user_id: int | None
    full_name: str
    study_level: str
    specialty: str
    photo_url: str | None
    created_at: datetime


class HackathonTeamMemberCreate(BaseModel):
    full_name: str
    study_level: str
    specialty: str
    user_id: int | None = None


class HackathonTeamMemberUpdate(BaseModel):
    full_name: str | None = None
    study_level: str | None = None
    specialty: str | None = None
    user_id: int | None = None


class HackathonTeamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    university_name: str
    name: str
    project_name: str
    project_description: str
    created_at: datetime
    members: list[HackathonTeamMemberRead] = []


class HackathonTeamCreate(BaseModel):
    university_name: str
    name: str
    project_name: str
    project_description: str


class HackathonTeamUpdate(BaseModel):
    university_name: str | None = None
    name: str | None = None
    project_name: str | None = None
    project_description: str | None = None
