"""payOS SDK exceptions."""

from typing import Any, Optional

import httpx


class PayOSError(Exception):
    """Base exception class for all payOS errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class APIError(PayOSError):
    """Base class for API-related errors."""

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        error_desc: Optional[str] = None,
        response: Optional[httpx.Response] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.error_desc = error_desc
        self.response = response

    @classmethod
    def from_response(
        cls,
        response: httpx.Response,
        *,
        error_data: Optional[dict[str, Any]] = None,
        message: Optional[str] = None,
    ) -> "APIError":
        """Create an APIError from an httpx response."""
        status_code = response.status_code
        error_code = None
        error_desc = None

        if error_data:
            error_code = error_data.get("code")
            error_desc = error_data.get("desc")

        if not message:
            message = error_desc or f"HTTP {status_code} error"

        # Return specific error subclass based on status code
        if status_code == 400:
            return BadRequestError(
                message or "",
                status_code=status_code,
                error_code=error_code,
                error_desc=error_desc,
                response=response,
            )
        elif status_code == 401:
            return UnauthorizedError(
                message or "",
                status_code=status_code,
                error_code=error_code,
                error_desc=error_desc,
                response=response,
            )
        elif status_code == 403:
            return ForbiddenError(
                message or "",
                status_code=status_code,
                error_code=error_code,
                error_desc=error_desc,
                response=response,
            )
        elif status_code == 404:
            return NotFoundError(
                message or "",
                status_code=status_code,
                error_code=error_code,
                error_desc=error_desc,
                response=response,
            )
        elif status_code == 429:
            return TooManyRequestsError(
                message or "",
                status_code=status_code,
                error_code=error_code,
                error_desc=error_desc,
                response=response,
            )
        elif status_code >= 500:
            return InternalServerError(
                message or "",
                status_code=status_code,
                error_code=error_code,
                error_desc=error_desc,
                response=response,
            )
        else:
            return cls(
                message or "",
                status_code=status_code,
                error_code=error_code,
                error_desc=error_desc,
                response=response,
            )


class BadRequestError(APIError):
    """400 Bad Request error."""

    pass


class UnauthorizedError(APIError):
    """401 Unauthorized error."""

    pass


class ForbiddenError(APIError):
    """403 Forbidden error."""

    pass


class NotFoundError(APIError):
    """404 Not Found error."""

    pass


class TooManyRequestsError(APIError):
    """429 Too Many Requests error."""

    pass


class InternalServerError(APIError):
    """5xx Internal Server error."""

    pass


class ConnectionError(PayOSError):
    """Network connection error."""

    pass


class ConnectionTimeoutError(PayOSError):
    """Network timeout error."""

    pass


class InvalidSignatureError(PayOSError):
    """Invalid signature error."""

    pass


class WebhookError(PayOSError):
    """Webhook-related error."""

    pass
