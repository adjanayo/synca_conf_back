from typing import Literal

from pydantic import BaseModel


class PaymentWebhookPayload(BaseModel):
    payment_id: int
    transaction_ref: str
    status: Literal["completed", "failed"]
