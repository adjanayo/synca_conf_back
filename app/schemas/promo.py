from pydantic import BaseModel


class PromoValidateRequest(BaseModel):
    code: str


class PromoValidateResponse(BaseModel):
    code: str
    discount_pct: int
    discount_fixed: int | None
