from typing import Literal

from pydantic import BaseModel

from app.models.payments import PAYMENT_METHOD_VALUES


class PaymentCreate(BaseModel):
    user_id: int
    # Not listed in schema.md §3B's field table, but payments.pass_type_id
    # is NOT NULL in the schema itself -- the frontend already collected it
    # at registration (§3A), so it's passed through here rather than
    # invented via a lookup the data model doesn't support (users has no
    # pass_type_id column).
    pass_type_id: int
    payment_method: Literal[*PAYMENT_METHOD_VALUES]
    promo_code: str | None = None
