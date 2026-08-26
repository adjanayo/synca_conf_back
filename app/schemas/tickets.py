import datetime

from pydantic import BaseModel, ConfigDict


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_number: str
    pdf_url: str | None
    is_scanned: bool
    created_at: datetime.datetime
