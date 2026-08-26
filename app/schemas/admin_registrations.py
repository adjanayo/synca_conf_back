import datetime

from pydantic import BaseModel


class RegistrationRead(BaseModel):
    payment_id: int
    user_id: int
    user_name: str
    user_email: str
    pass_type_name: str
    amount_paid: int
    status: str
    ticket_number: str | None
    created_at: datetime.datetime
