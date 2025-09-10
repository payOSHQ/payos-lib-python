"""Base resource class for API resources."""

from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from .._async_client import AsyncPayOS
    from .._client import PayOS

T = TypeVar("T")


class BaseResource:
    """Base class for API resources."""

    def __init__(self, client: "PayOS") -> None:
        self._client = client


class AsyncBaseResource:
    """Base class for async API resources."""

    def __init__(self, client: "AsyncPayOS") -> None:
        self._client = client
