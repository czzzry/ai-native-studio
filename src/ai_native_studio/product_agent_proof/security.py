"""Authentication and freshness checks for Linear-style webhooks."""

import hashlib
import hmac


class WebhookSecurityError(ValueError):
    """Base class for rejected webhook security checks."""

    code = "security_error"


class MissingSignatureError(WebhookSecurityError):
    code = "missing_signature"


class InvalidSignatureError(WebhookSecurityError):
    code = "invalid_signature"


class StaleTimestampError(WebhookSecurityError):
    code = "stale_timestamp"


def create_signature(secret: bytes, raw_body: bytes) -> str:
    """Create the Linear-compatible HMAC-SHA256 signature for a raw request body."""

    return hmac.new(secret, raw_body, hashlib.sha256).hexdigest()


def verify_signature(secret: bytes, raw_body: bytes, supplied_signature: str | None) -> None:
    """Verify the raw request body before trusting its parsed contents."""

    if not supplied_signature:
        raise MissingSignatureError("The Linear-Signature header is required.")

    expected = create_signature(secret, raw_body)
    if not hmac.compare_digest(expected, supplied_signature):
        raise InvalidSignatureError("The webhook signature does not match the request body.")


def verify_timestamp(timestamp_ms: int, now_ms: int, tolerance_seconds: int) -> None:
    """Reject events outside the symmetric freshness window."""

    difference_ms = abs(now_ms - timestamp_ms)
    if difference_ms > tolerance_seconds * 1000:
        raise StaleTimestampError(
            f"The webhook timestamp is outside the {tolerance_seconds}-second tolerance."
        )
