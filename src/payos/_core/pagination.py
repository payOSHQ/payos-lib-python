"""Pagination support for payOS API."""

# mypy: disable-error-code=redundant-cast

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING, Any, Generic, Optional, TypeVar, cast

from .models import PayOSBaseModel
from .request_options import (
    FinalRequestOptions,
    HTTPMethod,
    SignatureRequestType,
    SignatureResponseType,
)

if TYPE_CHECKING:
    from .._async_client import AsyncPayOS
    from .._client import PayOS

T = TypeVar("T")
ResponseT = TypeVar("ResponseT")


class PaginationParams(PayOSBaseModel):
    """Parameters for paginated requests."""

    limit: Optional[int] = 10
    offset: Optional[int] = 0


class Pagination(PayOSBaseModel):
    """Pagination metadata."""

    limit: int
    offset: int
    total: int
    count: int
    has_more: bool


class Page(Generic[T]):
    """Base class for paginated responses."""

    def __init__(
        self,
        client: "PayOS",
        cast_to: type[ResponseT],
        data: list[T],
        pagination: Pagination,
        options: FinalRequestOptions,
    ) -> None:
        self._client = client
        self.cast_to = cast_to
        self._data = data
        self._pagination = pagination
        self._options = options

    @property
    def data(self) -> list[T]:
        """The items in the current page."""
        return self._data

    @property
    def pagination(self) -> Pagination:
        """Pagination information for the current page."""
        return self._pagination

    def has_next_page(self) -> bool:
        """Check if there are more pages available."""
        return self._pagination.has_more

    def has_previous_page(self) -> bool:
        """Check if there are previous pages available."""
        return self._pagination.offset > 0

    def get_next_page(self) -> "Page[T]":
        """Get the next page of results."""
        if not self.has_next_page():
            raise ValueError("No more pages available")

        next_offset = self._pagination.offset + self._pagination.count
        next_options = FinalRequestOptions(
            method=cast(HTTPMethod, self._options.method),
            path=self._options.path,
            query={
                **(self._options.query or {}),
                "offset": next_offset,
                "limit": self._pagination.limit,
            },
            headers=self._options.headers,
            body=self._options.body,
            timeout=self._options.timeout,
            max_retries=self._options.max_retries,
            signature_request=cast(Optional[SignatureRequestType], self._options.signature_request),
            signature_response=cast(
                Optional[SignatureResponseType], self._options.signature_response
            ),
        )

        response = self._client.request(next_options, cast_to=self.cast_to)
        return self._create_page_instance(self._client, self.cast_to, response, next_options)

    def get_previous_page(self) -> "Page[T]":
        """Get the previous page of results."""
        if not self.has_previous_page():
            raise ValueError("No previous pages available")

        prev_offset = max(0, self._pagination.offset - self._pagination.limit)
        prev_options = FinalRequestOptions(
            method=cast(HTTPMethod, self._options.method),
            path=self._options.path,
            query={
                **(self._options.query or {}),
                "offset": prev_offset,
                "limit": self._pagination.limit,
            },
            headers=self._options.headers,
            body=self._options.body,
            timeout=self._options.timeout,
            max_retries=self._options.max_retries,
            signature_request=cast(Optional[SignatureRequestType], self._options.signature_request),
            signature_response=cast(
                Optional[SignatureResponseType], self._options.signature_response
            ),
        )

        response = self._client.request(prev_options, cast_to=self.cast_to)
        return self._create_page_instance(self._client, self.cast_to, response, prev_options)

    def _create_page_instance(
        self, client: Any, cast_to: type[ResponseT], data: Any, options: FinalRequestOptions
    ) -> "Page[T]":
        """Create a new page instance. Override in subclasses for custom page types."""
        # Handle both dict and Pydantic model responses
        if hasattr(data, "pagination"):
            # Pydantic model
            pagination = data.pagination
            # Find the first list attribute (excluding pagination)
            items = []
            for attr_name in dir(data):
                if not attr_name.startswith("_") and attr_name != "pagination":
                    attr_value = getattr(data, attr_name)
                    if isinstance(attr_value, list):
                        items = attr_value
                        break
        else:
            # Dict format
            pagination_data = data.get("pagination", {})
            pagination = Pagination.model_validate(pagination_data)
            # Find the first list property in data (excluding pagination)
            items = []
            for key, value in data.items():
                if key != "pagination" and isinstance(value, list):
                    items = value
                    break

        return Page(client, cast_to, items, pagination, options)

    def iter_all(self) -> Iterator[T]:
        """Iterate over all items across all pages."""
        current_page = self

        while True:
            yield from current_page.data

            if not current_page.has_next_page():
                break

            current_page = current_page.get_next_page()

    def to_list(self) -> list[T]:
        """Collect all items from all pages into a list."""
        return list(self.iter_all())

    def __iter__(self) -> Iterator[T]:
        """Make Page directly iterable."""
        return self.iter_all()


class AsyncPage(Generic[T]):
    """Base class for async paginated responses."""

    def __init__(
        self,
        client: "AsyncPayOS",
        cast_to: type[ResponseT],
        data: list[T],
        pagination: Pagination,
        options: FinalRequestOptions,
    ) -> None:
        self._client = client
        self.cast_to = cast_to
        self._data = data
        self._pagination = pagination
        self._options = options

    @property
    def data(self) -> list[T]:
        """The items in the current page."""
        return self._data

    @property
    def pagination(self) -> Pagination:
        """Pagination information for the current page."""
        return self._pagination

    def has_next_page(self) -> bool:
        """Check if there are more pages available."""
        return self._pagination.has_more

    def has_previous_page(self) -> bool:
        """Check if there are previous pages available."""
        return self._pagination.offset > 0

    async def get_next_page(self) -> "AsyncPage[T]":
        """Get the next page of results."""
        if not self.has_next_page():
            raise ValueError("No more pages available")

        next_offset = self._pagination.offset + self._pagination.count
        next_options = FinalRequestOptions(
            method=cast(HTTPMethod, self._options.method),
            path=self._options.path,
            query={
                **(self._options.query or {}),
                "offset": next_offset,
                "limit": self._pagination.limit,
            },
            headers=self._options.headers,
            body=self._options.body,
            timeout=self._options.timeout,
            max_retries=self._options.max_retries,
            signature_request=cast(Optional[SignatureRequestType], self._options.signature_request),
            signature_response=cast(
                Optional[SignatureResponseType], self._options.signature_response
            ),
        )

        response = await self._client.request(next_options, cast_to=self.cast_to)
        return self._create_page_instance(self._client, self.cast_to, response, next_options)

    async def get_previous_page(self) -> "AsyncPage[T]":
        """Get the previous page of results."""
        if not self.has_previous_page():
            raise ValueError("No previous pages available")

        prev_offset = max(0, self._pagination.offset - self._pagination.limit)
        prev_options = FinalRequestOptions(
            method=cast(HTTPMethod, self._options.method),
            path=self._options.path,
            query={
                **(self._options.query or {}),
                "offset": prev_offset,
                "limit": self._pagination.limit,
            },
            headers=self._options.headers,
            body=self._options.body,
            timeout=self._options.timeout,
            max_retries=self._options.max_retries,
            signature_request=cast(Optional[SignatureRequestType], self._options.signature_request),
            signature_response=cast(
                Optional[SignatureResponseType], self._options.signature_response
            ),
        )

        response = await self._client.request(prev_options, cast_to=self.cast_to)
        return self._create_page_instance(self._client, self.cast_to, response, prev_options)

    def _create_page_instance(
        self, client: Any, cast_to: type[ResponseT], data: Any, options: FinalRequestOptions
    ) -> "AsyncPage[T]":
        """Create a new page instance. Override in subclasses for custom page types."""
        # Handle both dict and Pydantic model responses
        if hasattr(data, "pagination"):
            # Pydantic model
            pagination = data.pagination
            # Find the first list attribute (excluding pagination)
            items = []
            for attr_name in dir(data):
                if not attr_name.startswith("_") and attr_name != "pagination":
                    attr_value = getattr(data, attr_name)
                    if isinstance(attr_value, list):
                        items = attr_value
                        break
        else:
            # Dict format
            pagination_data = data.get("pagination", {})
            pagination = Pagination.model_validate(pagination_data)
            # Find the first list property in data (excluding pagination)
            items = []
            for key, value in data.items():
                if key != "pagination" and isinstance(value, list):
                    items = value
                    break

        return AsyncPage(client, cast_to, items, pagination, options)

    async def iter_all(self) -> AsyncIterator[T]:
        """Async iterate over all items across all pages."""
        current_page = self

        while True:
            for item in current_page.data:
                yield item

            if not current_page.has_next_page():
                break

            current_page = await current_page.get_next_page()

    async def to_list(self) -> list[T]:
        """Collect all items from all pages into a list."""
        items = []
        async for item in self.iter_all():
            items.append(item)
        return items

    def __aiter__(self) -> AsyncIterator[T]:
        """Make AsyncPage directly async iterable."""
        return self.iter_all()
