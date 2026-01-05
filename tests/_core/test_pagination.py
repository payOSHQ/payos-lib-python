"""Tests for pagination."""

from unittest.mock import Mock

import pytest

from payos import AsyncPayOS, PayOS
from payos._core.pagination import AsyncPage, Page, Pagination
from payos._core.request_options import FinalRequestOptions


class TestSyncPagination:
    """Test synchronous pagination."""

    def test_constructs_empty_page_when_no_data(self):
        """Test constructing empty page when no items."""
        client = PayOS(client_id="c", api_key="k", checksum_key="s")
        options = FinalRequestOptions(method="GET", path="/v1/test")

        # Create page with empty data
        pagination = Pagination(limit=10, offset=0, total=0, count=0, has_more=False)
        page = Page(client=client, cast_to=dict, data=[], pagination=pagination, options=options)

        assert page.data == []
        assert page.pagination.count == 0
        assert page.pagination.total == 0
        assert not page.has_next_page()

    def test_has_next_page_logic(self):
        """Test hasNextPage returns correct value based on pagination data."""
        client = PayOS(client_id="c", api_key="k", checksum_key="s")
        options = FinalRequestOptions(method="GET", path="/v1/test", query={"offset": 0})

        # Page with more data available
        pagination = Pagination(limit=2, offset=0, total=4, count=2, has_more=True)
        page = Page(
            client=client,
            cast_to=dict,
            data=["a", "b"],
            pagination=pagination,
            options=options,
        )

        assert page.has_next_page() is True

        # Page with no more data
        pagination_no_more = Pagination(limit=2, offset=2, total=4, count=2, has_more=False)
        page_no_more = Page(
            client=client,
            cast_to=dict,
            data=["c", "d"],
            pagination=pagination_no_more,
            options=options,
        )

        assert page_no_more.has_next_page() is False

    def test_has_previous_page_logic(self):
        """Test hasPreviousPage returns correct value based on offset."""
        client = PayOS(client_id="c", api_key="k", checksum_key="s")
        options = FinalRequestOptions(method="GET", path="/v1/test", query={"offset": 0})

        # First page (offset=0)
        pagination_first = Pagination(limit=2, offset=0, total=4, count=2, has_more=True)
        page_first = Page(
            client=client,
            cast_to=dict,
            data=["a", "b"],
            pagination=pagination_first,
            options=options,
        )

        assert page_first.has_previous_page() is False

        # Second page (offset=2)
        pagination_second = Pagination(limit=2, offset=2, total=4, count=2, has_more=False)
        page_second = Page(
            client=client,
            cast_to=dict,
            data=["c", "d"],
            pagination=pagination_second,
            options=options,
        )

        assert page_second.has_previous_page() is True

    def test_get_next_page_calls_client_request(self):
        """Test getNextPage calls client.request with updated offset."""
        client = PayOS(client_id="c", api_key="k", checksum_key="s")
        options = FinalRequestOptions(method="GET", path="/v1/test", query={"offset": 0})

        # First page
        pagination = Pagination(limit=2, offset=0, total=4, count=2, has_more=True)
        page = Page(
            client=client,
            cast_to=dict,
            data=["a", "b"],
            pagination=pagination,
            options=options,
        )

        # Mock the request method
        next_page_data = {
            "items": ["c", "d"],
            "pagination": {"limit": 2, "offset": 2, "total": 4, "count": 2, "hasMore": False},
        }
        mock_request = Mock(return_value=next_page_data)
        client.request = mock_request

        # Get next page
        next_page = page.get_next_page()

        # Verify client.request was called
        assert mock_request.called
        assert next_page.data == ["c", "d"]
        assert next_page.pagination.offset == 2
        assert not next_page.has_next_page()

    def test_get_next_page_raises_error_when_no_more_pages(self):
        """Test getNextPage raises ValueError when no more pages available."""
        client = PayOS(client_id="c", api_key="k", checksum_key="s")
        options = FinalRequestOptions(method="GET", path="/v1/test")

        # Last page
        pagination = Pagination(limit=2, offset=2, total=4, count=2, has_more=False)
        page = Page(
            client=client,
            cast_to=dict,
            data=["c", "d"],
            pagination=pagination,
            options=options,
        )

        with pytest.raises(ValueError, match="No more pages available"):
            page.get_next_page()

    def test_get_previous_page_calls_client_request(self):
        """Test getPreviousPage calls client.request with updated offset."""
        client = PayOS(client_id="c", api_key="k", checksum_key="s")
        options = FinalRequestOptions(method="GET", path="/v1/test", query={"offset": 2})

        # Second page
        pagination = Pagination(limit=2, offset=2, total=4, count=2, has_more=False)
        page = Page(
            client=client,
            cast_to=dict,
            data=["c", "d"],
            pagination=pagination,
            options=options,
        )

        # Mock the request method
        prev_page_data = {
            "items": ["a", "b"],
            "pagination": {"limit": 2, "offset": 0, "total": 4, "count": 2, "hasMore": True},
        }
        mock_request = Mock(return_value=prev_page_data)
        client.request = mock_request

        # Get previous page
        prev_page = page.get_previous_page()

        # Verify client.request was called
        assert mock_request.called
        assert prev_page.data == ["a", "b"]
        assert prev_page.pagination.offset == 0

    def test_get_previous_page_raises_error_when_no_previous_pages(self):
        """Test getPreviousPage raises ValueError when at first page."""
        client = PayOS(client_id="c", api_key="k", checksum_key="s")
        options = FinalRequestOptions(method="GET", path="/v1/test", query={"offset": 0})

        # First page
        pagination = Pagination(limit=2, offset=0, total=4, count=2, has_more=True)
        page = Page(
            client=client,
            cast_to=dict,
            data=["a", "b"],
            pagination=pagination,
            options=options,
        )

        with pytest.raises(ValueError, match="No previous pages available"):
            page.get_previous_page()

    def test_iter_all_collects_all_items_via_paging(self):
        """Test iterating over all pages collects all items."""
        client = PayOS(client_id="c", api_key="k", checksum_key="s")
        options = FinalRequestOptions(method="GET", path="/v1/test")

        # First page
        pagination1 = Pagination(limit=2, offset=0, total=4, count=2, has_more=True)
        page1 = Page(
            client=client,
            cast_to=dict,
            data=["a", "b"],
            pagination=pagination1,
            options=options,
        )

        # Mock second page response
        page2_data = {
            "items": ["c", "d"],
            "pagination": {"limit": 2, "offset": 2, "total": 4, "count": 2, "hasMore": False},
        }
        mock_request = Mock(return_value=page2_data)
        client.request = mock_request

        # Collect all items
        collected = list(page1.iter_all())

        assert collected == ["a", "b", "c", "d"]

    def test_to_list_collects_all_items(self):
        """Test to_list method collects all items from all pages."""
        client = PayOS(client_id="c", api_key="k", checksum_key="s")
        options = FinalRequestOptions(method="GET", path="/v1/test")

        # First page
        pagination1 = Pagination(limit=2, offset=0, total=4, count=2, has_more=True)
        page1 = Page(
            client=client,
            cast_to=dict,
            data=["a", "b"],
            pagination=pagination1,
            options=options,
        )

        # Mock second page response
        page2_data = {
            "items": ["c", "d"],
            "pagination": {"limit": 2, "offset": 2, "total": 4, "count": 2, "hasMore": False},
        }
        mock_request = Mock(return_value=page2_data)
        client.request = mock_request

        # Collect all items using to_list
        result = page1.to_list()

        assert result == ["a", "b", "c", "d"]

    def test_page_is_directly_iterable(self):
        """Test that Page is directly iterable using for loop."""
        client = PayOS(client_id="c", api_key="k", checksum_key="s")
        options = FinalRequestOptions(method="GET", path="/v1/test")

        # First page
        pagination1 = Pagination(limit=2, offset=0, total=4, count=2, has_more=True)
        page1 = Page(
            client=client,
            cast_to=dict,
            data=["a", "b"],
            pagination=pagination1,
            options=options,
        )

        # Mock second page response
        page2_data = {
            "items": ["c", "d"],
            "pagination": {"limit": 2, "offset": 2, "total": 4, "count": 2, "hasMore": False},
        }
        mock_request = Mock(return_value=page2_data)
        client.request = mock_request

        # Use for loop directly on page
        collected = []
        for item in page1:
            collected.append(item)

        assert collected == ["a", "b", "c", "d"]


class TestAsyncPagination:
    """Test asynchronous pagination."""

    @pytest.mark.asyncio
    async def test_constructs_empty_page_when_no_data(self):
        """Test constructing empty async page when no items."""
        client = AsyncPayOS(client_id="c", api_key="k", checksum_key="s")
        options = FinalRequestOptions(method="GET", path="/v1/test")

        # Create page with empty data
        pagination = Pagination(limit=10, offset=0, total=0, count=0, has_more=False)
        page = AsyncPage(
            client=client, cast_to=dict, data=[], pagination=pagination, options=options
        )

        assert page.data == []
        assert page.pagination.count == 0
        assert not page.has_next_page()

    @pytest.mark.asyncio
    async def test_has_next_page_and_has_previous_page_logic(self):
        """Test async page has_next_page and has_previous_page logic."""
        client = AsyncPayOS(client_id="c", api_key="k", checksum_key="s")
        options = FinalRequestOptions(method="GET", path="/v1/test", query={"offset": 0})

        # First page
        pagination = Pagination(limit=2, offset=0, total=4, count=2, has_more=True)
        page = AsyncPage(
            client=client,
            cast_to=dict,
            data=["a", "b"],
            pagination=pagination,
            options=options,
        )

        assert page.has_next_page() is True
        assert page.has_previous_page() is False

    @pytest.mark.asyncio
    async def test_get_next_page_calls_client_request(self):
        """Test async getNextPage calls client.request with updated offset."""
        client = AsyncPayOS(client_id="c", api_key="k", checksum_key="s")
        options = FinalRequestOptions(method="GET", path="/v1/test", query={"offset": 0})

        # First page
        pagination = Pagination(limit=2, offset=0, total=4, count=2, has_more=True)
        page = AsyncPage(
            client=client,
            cast_to=dict,
            data=["a", "b"],
            pagination=pagination,
            options=options,
        )

        # Mock the request method
        next_page_data = {
            "items": ["c", "d"],
            "pagination": {"limit": 2, "offset": 2, "total": 4, "count": 2, "hasMore": False},
        }

        async def mock_request(*args, **kwargs):
            return next_page_data

        client.request = mock_request

        # Get next page
        next_page = await page.get_next_page()

        assert next_page.data == ["c", "d"]
        assert next_page.pagination.offset == 2
        assert not next_page.has_next_page()

    @pytest.mark.asyncio
    async def test_get_next_page_raises_error_when_no_more_pages(self):
        """Test async getNextPage raises ValueError when no more pages available."""
        client = AsyncPayOS(client_id="c", api_key="k", checksum_key="s")
        options = FinalRequestOptions(method="GET", path="/v1/test")

        # Last page
        pagination = Pagination(limit=2, offset=2, total=4, count=2, has_more=False)
        page = AsyncPage(
            client=client,
            cast_to=dict,
            data=["c", "d"],
            pagination=pagination,
            options=options,
        )

        with pytest.raises(ValueError, match="No more pages available"):
            await page.get_next_page()

    @pytest.mark.asyncio
    async def test_get_previous_page_calls_client_request(self):
        """Test async getPreviousPage calls client.request with updated offset."""
        client = AsyncPayOS(client_id="c", api_key="k", checksum_key="s")
        options = FinalRequestOptions(method="GET", path="/v1/test", query={"offset": 2})

        # Second page
        pagination = Pagination(limit=2, offset=2, total=4, count=2, has_more=False)
        page = AsyncPage(
            client=client,
            cast_to=dict,
            data=["c", "d"],
            pagination=pagination,
            options=options,
        )

        # Mock the request method
        prev_page_data = {
            "items": ["a", "b"],
            "pagination": {"limit": 2, "offset": 0, "total": 4, "count": 2, "hasMore": True},
        }

        async def mock_request(*args, **kwargs):
            return prev_page_data

        client.request = mock_request

        # Get previous page
        prev_page = await page.get_previous_page()

        assert prev_page.data == ["a", "b"]
        assert prev_page.pagination.offset == 0

    @pytest.mark.asyncio
    async def test_async_iteration_collects_all_items(self):
        """Test async iteration over all pages collects all items."""
        client = AsyncPayOS(client_id="c", api_key="k", checksum_key="s")
        options = FinalRequestOptions(method="GET", path="/v1/test")

        # First page
        pagination1 = Pagination(limit=2, offset=0, total=4, count=2, has_more=True)
        page1 = AsyncPage(
            client=client,
            cast_to=dict,
            data=["a", "b"],
            pagination=pagination1,
            options=options,
        )

        # Mock second page response
        page2_data = {
            "items": ["c", "d"],
            "pagination": {"limit": 2, "offset": 2, "total": 4, "count": 2, "hasMore": False},
        }

        async def mock_request(*args, **kwargs):
            return page2_data

        client.request = mock_request

        # Collect all items using async for
        collected = []
        async for item in page1:
            collected.append(item)

        assert collected == ["a", "b", "c", "d"]

    @pytest.mark.asyncio
    async def test_to_list_collects_all_items(self):
        """Test async to_list method collects all items from all pages."""
        client = AsyncPayOS(client_id="c", api_key="k", checksum_key="s")
        options = FinalRequestOptions(method="GET", path="/v1/test")

        # First page
        pagination1 = Pagination(limit=2, offset=0, total=4, count=2, has_more=True)
        page1 = AsyncPage(
            client=client,
            cast_to=dict,
            data=["a", "b"],
            pagination=pagination1,
            options=options,
        )

        # Mock second page response
        page2_data = {
            "items": ["c", "d"],
            "pagination": {"limit": 2, "offset": 2, "total": 4, "count": 2, "hasMore": False},
        }

        async def mock_request(*args, **kwargs):
            return page2_data

        client.request = mock_request

        # Collect all items using to_list
        result = await page1.to_list()

        assert result == ["a", "b", "c", "d"]
