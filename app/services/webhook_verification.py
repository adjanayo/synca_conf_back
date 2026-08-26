import hashlib
import hmac
import time

STRIPE_TOLERANCE_SECONDS = 300


class InvalidWebhookSignatureError(Exception):
    pass


def verify_stripe_signature(payload: bytes, sig_header: str, secret: str) -> None:
    """Verify a Stripe webhook using Stripe's documented scheme.

    The `Stripe-Signature` header looks like `t=<timestamp>,v1=<hex hmac>`.
    The signed value is `"{timestamp}.{raw body}"`, HMAC-SHA256'd with the
    webhook's signing secret.
    """
    if not secret:
        # An unset secret must fail closed, not verify against "" -- an
        # empty string is itself a trivially known HMAC key, so this isn't
        # "skip verification", it's "accept a forged signature from anyone".
        raise InvalidWebhookSignatureError("Secret webhook non configuré.")

    parts = dict(item.split("=", 1) for item in sig_header.split(",") if "=" in item)
    timestamp = parts.get("t")
    signature = parts.get("v1")
    if timestamp is None or signature is None:
        raise InvalidWebhookSignatureError("En-tête de signature malformé.")

    try:
        if abs(time.time() - int(timestamp)) > STRIPE_TOLERANCE_SECONDS:
            raise InvalidWebhookSignatureError("Signature expirée.")
    except ValueError as exc:
        raise InvalidWebhookSignatureError("Horodatage de signature invalide.") from exc

    signed_payload = f"{timestamp}.".encode() + payload
    expected = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise InvalidWebhookSignatureError("Signature invalide.")


def verify_hmac_signature(payload: bytes, signature: str, secret: str) -> None:
    """Generic HMAC-SHA256 hex-digest verification (Wave / Orange Money).

    Assumes the common "HMAC-SHA256 over the raw request body" pattern most
    payment webhooks use. This project has no real Wave/Orange Money
    credentials or docs -- confirm the exact scheme against their live API
    reference before accepting production traffic.
    """
    if not secret:
        raise InvalidWebhookSignatureError("Secret webhook non configuré.")

    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise InvalidWebhookSignatureError("Signature invalide.")
