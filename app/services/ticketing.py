import uuid


def generate_ticket_number(payment_id: int) -> str:
    return f"SYNCA-{payment_id:06d}"


def generate_qr_code_hash() -> str:
    return uuid.uuid4().hex
