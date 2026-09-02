from datetime import datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.referentials import PassType

PAYMENT_METHOD_VALUES = ("stripe", "wave", "orange_money", "mtn", "bank_transfer")
PAYMENT_STATUS_VALUES = ("pending", "completed", "failed", "refunded")


class PromoCode(Base):
    __tablename__ = "promo_codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    discount_pct: Mapped[int] = mapped_column(Integer, nullable=False)
    discount_fixed: Mapped[int | None] = mapped_column(Integer)
    usage_limit: Mapped[int | None] = mapped_column(Integer)
    usage_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    valid_from: Mapped[datetime | None] = mapped_column(Date)
    valid_until: Mapped[datetime | None] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    pass_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("pass_types.id"), nullable=False)
    promo_code_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("promo_codes.id"))
    amount_original: Mapped[int] = mapped_column(Integer, nullable=False)
    amount_paid: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="XOF", server_default="XOF")
    payment_method: Mapped[str] = mapped_column(
        Enum(*PAYMENT_METHOD_VALUES, name="payment_method"), nullable=False
    )
    transaction_ref: Mapped[str | None] = mapped_column(String(255), unique=True)
    status: Mapped[str] = mapped_column(
        Enum(*PAYMENT_STATUS_VALUES, name="payment_status"),
        default="pending",
        server_default="pending",
        index=True,
    )
    paid_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    pass_type: Mapped[PassType] = relationship()


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    payment_id: Mapped[int] = mapped_column(Integer, ForeignKey("payments.id"), unique=True)
    pass_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("pass_types.id"), nullable=False)
    ticket_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    qr_code_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    pdf_url: Mapped[str | None] = mapped_column(String(255))
    is_scanned: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    scanned_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Waitlist(Base):
    __tablename__ = "waitlist"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    notified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    registered: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    last_notified_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
