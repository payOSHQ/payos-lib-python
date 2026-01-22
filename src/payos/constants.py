"""This module is deprecated and will be removed in v2.0.0.
The constants defined here are no longer part of the public API.

For error handling, use the exception classes from the main payos module:
    from payos import PayOSError, APIError, WebhookError, InvalidSignatureError

For the base URL, use the PayOS client's base_url attribute or environment variables.
"""

import warnings

warnings.warn(
    "The 'payos.constants' module is deprecated and will be removed in v2.0.0. "
    "Constants are no longer part of the public API. ",
    DeprecationWarning,
    stacklevel=2,
)

# Legacy error messages for backward compatibility
ERROR_MESSAGE = {
    "NO_SIGNATURE": "No signature.",
    "NO_DATA": "No data.",
    "INVALID_SIGNATURE": "Invalid signature.",
    "DATA_NOT_INTEGRITY": "The data is unreliable because the signature of the response does not match the signature of the data",
    "WEBHOOK_URL_INVALID": "Webhook URL invalid.",
    "UNAUTHORIZED": "Unauthorized.",
    "INTERNAL_SERVER_ERROR": "Internal Server Error.",
    "INVALID_PARAMETER": "Invalid Parameter.",
}

# Legacy error codes for backward compatibility
ERROR_CODE = {
    "INTERNAL_SERVER_ERROR": "20",
    "UNAUTHORIZED": "401",
}

# Legacy base URL constant
PAYOS_BASE_URL = "https://api-merchant.payos.vn"

__all__ = ["ERROR_MESSAGE", "ERROR_CODE", "PAYOS_BASE_URL"]
