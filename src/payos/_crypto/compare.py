"""Constant-time signature comparison."""

import hmac


def constant_time_equal(a: str, b: str) -> bool:
    try:
        a_bytes = a.encode("utf-8")
        b_bytes = b.encode("utf-8")
    except UnicodeEncodeError:
        # Lone surrogates cannot be a valid hex signature; treat as mismatch.
        return False
    return hmac.compare_digest(a_bytes, b_bytes)
