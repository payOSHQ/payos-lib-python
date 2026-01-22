"""This module is deprecated and will be removed in v2.0.0.
Import PayOSError from the main payos module instead:

    from payos import PayOSError

For more specific error handling, use:
    from payos import APIError, WebhookError, InvalidSignatureError
"""

import warnings

warnings.warn(
    "The 'payos.custom_error' module is deprecated and will be removed in v2.0.0. "
    "Import PayOSError from 'payos' directly instead: from payos import PayOSError. ",
    DeprecationWarning,
    stacklevel=2,
)


class PayOSError(Exception):
    """Legacy PayOSError class.

    .. deprecated:: 1.0.0
        Use APIError from 'payos' module instead.
        This class will be removed in v2.0.0.

    The v0.x PayOSError accepted (code, message) parameters.
    """

    def __init__(self, code: str, message: str) -> None:
        """Initialize PayOSError with legacy signature.

        Args:
            code: Error code (e.g., "20", "401").
            message: Error message.
        """
        super().__init__(message)
        self.code = code


__all__ = ["PayOSError"]
