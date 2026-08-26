import hashlib
import hmac
import time

import pytest

from app.services.webhook_verification import (
    InvalidWebhookSignatureError,
    verify_hmac_signature,
    verify_stripe_signature,
)


def test_verify_hmac_signature_accepts_valid():
    secret = "shh"
    body = b'{"a": 1}'
    signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    verify_hmac_signature(body, signature, secret)  # should not raise


def test_verify_hmac_signature_rejects_invalid():
    with pytest.raises(InvalidWebhookSignatureError):
        verify_hmac_signature(b'{"a": 1}', "wrong", "shh")


def test_verify_stripe_signature_accepts_valid():
    secret = "stripe-secret"
    body = b'{"a": 1}'
    timestamp = str(int(time.time()))
    signed_payload = f"{timestamp}.".encode() + body
    sig = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    header = f"t={timestamp},v1={sig}"
    verify_stripe_signature(body, header, secret)  # should not raise


def test_verify_stripe_signature_rejects_bad_signature():
    timestamp = str(int(time.time()))
    header = f"t={timestamp},v1=wrong"
    with pytest.raises(InvalidWebhookSignatureError):
        verify_stripe_signature(b'{"a": 1}', header, "stripe-secret")


def test_verify_stripe_signature_rejects_expired_timestamp():
    secret = "stripe-secret"
    body = b'{"a": 1}'
    old_timestamp = str(int(time.time()) - 1000)
    signed_payload = f"{old_timestamp}.".encode() + body
    sig = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    header = f"t={old_timestamp},v1={sig}"
    with pytest.raises(InvalidWebhookSignatureError):
        verify_stripe_signature(body, header, secret)


def test_verify_stripe_signature_rejects_malformed_header():
    with pytest.raises(InvalidWebhookSignatureError):
        verify_stripe_signature(b"{}", "garbage-header", "secret")


def test_verify_hmac_signature_rejects_empty_secret_even_with_matching_forged_signature():
    # An empty secret must fail closed, not "verify successfully against an
    # empty key" -- anyone can compute HMAC(key=b"", body) themselves.
    body = b'{"a": 1}'
    forged_signature = hmac.new(b"", body, hashlib.sha256).hexdigest()
    with pytest.raises(InvalidWebhookSignatureError):
        verify_hmac_signature(body, forged_signature, "")


def test_verify_stripe_signature_rejects_empty_secret_even_with_matching_forged_signature():
    body = b'{"a": 1}'
    timestamp = str(int(time.time()))
    forged_sig = hmac.new(b"", f"{timestamp}.".encode() + body, hashlib.sha256).hexdigest()
    header = f"t={timestamp},v1={forged_sig}"
    with pytest.raises(InvalidWebhookSignatureError):
        verify_stripe_signature(body, header, "")
