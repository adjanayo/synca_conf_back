from typing import Literal

from pydantic import BaseModel

from app.models.applications import APPLICATION_STATUS_VALUES, NEGOTIATION_STATUS_VALUES


class SpeakerStatusUpdate(BaseModel):
    status: Literal[*APPLICATION_STATUS_VALUES]


class AmbassadorStatusUpdate(BaseModel):
    status: Literal[*APPLICATION_STATUS_VALUES]


class PartnerStatusUpdate(BaseModel):
    status: Literal[*NEGOTIATION_STATUS_VALUES]


class ExhibitorStatusUpdate(BaseModel):
    status: Literal[*NEGOTIATION_STATUS_VALUES]
