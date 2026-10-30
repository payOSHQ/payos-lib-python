"""Safe path segments for identifiers interpolated into API paths."""

from typing import Any
from urllib.parse import quote

from .._core.exceptions import PayOSError

_MAX_SAFE_INTEGER = 2**53 - 1


def encode_path_segment(name: str, value: Any) -> str:
    """Return ``value`` as a single percent-encoded URL path segment.

    Identifiers are interpolated into paths such as ``/v2/payment-requests/{id}/cancel``. Without
    encoding, a value like ``../../v1/payouts-account/balance`` or ``x?`` re-targets the
    authenticated request to another endpoint, so strings are percent-encoded and ``.``/``..``
    segments are rejected. Integers must be non-negative and within the safe integer range.

    Raises:
        PayOSError: when the value is empty, a dot segment, or not a supported type/range.
    """
    if isinstance(value, bool):
        raise PayOSError(f"{name} must be a non-empty string or a safe integer")
    if isinstance(value, int):
        if value < 0 or value > _MAX_SAFE_INTEGER:
            raise PayOSError(f"{name} must be a non-negative safe integer")
        return str(value)
    if not isinstance(value, str) or not value:
        raise PayOSError(f"{name} must be a non-empty string or a safe integer")
    if value in (".", ".."):
        raise PayOSError(f"{name} must not be a dot segment")
    return quote(value, safe="")
