from pydantic import BaseModel


class AdminStatsRead(BaseModel):
    total_registrations: int
    total_revenue: int
    completed_payments: int
    payments_with_promo: int
    promo_conversion_rate: float
    applications_by_status: dict[str, dict[str, int]]
