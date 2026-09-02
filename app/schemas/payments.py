import datetime

from pydantic import BaseModel, ConfigDict


class PromoCodeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    discount_pct: int
    discount_fixed: int | None
    usage_limit: int | None
    usage_count: int
    valid_from: datetime.date | None
    valid_until: datetime.date | None
    is_active: bool
    created_at: datetime.datetime


class PromoCodeCreate(BaseModel):
    code: str
    discount_pct: int = 0
    discount_fixed: int | None = None
    usage_limit: int | None = None
    valid_from: datetime.date | None = None
    valid_until: datetime.date | None = None
    is_active: bool = True


class PromoCodeUpdate(BaseModel):
    discount_pct: int | None = None
    discount_fixed: int | None = None
    usage_limit: int | None = None
    valid_from: datetime.date | None = None
    valid_until: datetime.date | None = None
    is_active: bool | None = None


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    pass_type_id: int
    promo_code_id: int | None
    amount_original: int
    amount_paid: int
    currency: str
    payment_method: str
    transaction_ref: str | None
    status: str
    paid_at: datetime.datetime | None
    created_at: datetime.datetime


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    payment_id: int
    pass_type_id: int
    ticket_number: str
    qr_code_hash: str
    pdf_url: str | None
    is_scanned: bool
    scanned_at: datetime.datetime | None
    created_at: datetime.datetime


class WaitlistRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    notified: bool
    registered: bool
    created_at: datetime.datetime
