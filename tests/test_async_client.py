"""Tests for asynchronous AsyncPayOS client."""

from typing import Any

import httpx
import pytest
from pytest_httpx import HTTPXMock

from payos import (
    AsyncPayOS,
    PayOSError,
    APIError,
    BadRequestError,
    UnauthorizedError,
    NotFoundError,
    InternalServerError,
    InvalidSignatureError,
)
from payos._client import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES

# Constants
CLIENT_ID = "test-client-id"
API_KEY = "test-api-key"
CHECKSUM_KEY = "test-checksum-key"
BASE_URL = "https://api-test.payos.vn"
PARTNER_CODE = "test-partner-code"


class TestAsyncPayOSInitialization:
    """Test AsyncPayOS client initialization."""

    def test_create_client_with_valid_credentials(self):
        """Test creating client with valid credentials."""
        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        assert client.client_id == CLIENT_ID
        assert client.api_key == API_KEY
        assert client.checksum_key == CHECKSUM_KEY
        assert client.base_url == BASE_URL

    def test_missing_client_id_raises_error(self):
        """Test that missing client_id raises PayOSError."""
        with pytest.raises(PayOSError, match="PAYOS_CLIENT_ID"):
            AsyncPayOS(
                api_key=API_KEY,
                checksum_key=CHECKSUM_KEY,
            )

    def test_missing_api_key_raises_error(self):
        """Test that missing api_key raises PayOSError."""
        with pytest.raises(PayOSError, match="PAYOS_API_KEY"):
            AsyncPayOS(
                client_id=CLIENT_ID,
                checksum_key=CHECKSUM_KEY,
            )

    def test_missing_checksum_key_raises_error(self):
        """Test that missing checksum_key raises PayOSError."""
        with pytest.raises(PayOSError, match="PAYOS_CHECKSUM_KEY"):
            AsyncPayOS(
                client_id=CLIENT_ID,
                api_key=API_KEY,
            )

    def test_default_timeout_and_max_retries(self):
        """Test default timeout and max_retries values."""
        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
        )

        assert client.timeout == DEFAULT_TIMEOUT
        assert client.max_retries == DEFAULT_MAX_RETRIES

    def test_override_timeout_and_max_retries(self):
        """Test overriding timeout and max_retries."""
        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            timeout=30.0,
            max_retries=1,
        )

        assert client.timeout == 30.0
        assert client.max_retries == 1

    def test_default_base_url(self):
        """Test default base URL when not provided."""
        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
        )

        assert client.base_url == DEFAULT_BASE_URL

    def test_partner_code_when_provided(self):
        """Test partner code is set when provided."""
        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            partner_code=PARTNER_CODE,
        )

        assert client.partner_code == PARTNER_CODE

    def test_partner_code_when_not_provided(self):
        """Test partner code is None when not provided."""
        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
        )

        assert client.partner_code is None

    def test_resources_initialized(self):
        """Test that resource properties are accessible."""
        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
        )

        assert client.payment_requests is not None
        assert client.payouts is not None
        assert client.payouts_account is not None
        assert client.webhooks is not None

    def test_user_agent(self):
        """Test user agent is correctly set."""
        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
        )

        assert "AsyncPayOS" in client.user_agent
        assert "Python" in client.user_agent

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test client can be used as context manager."""
        async with AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
        ) as client:
            assert client is not None


class TestAsyncPayOSHeaders:
    """Test header building."""

    @pytest.mark.asyncio
    async def test_build_headers_with_required_fields(self, httpx_mock: HTTPXMock):
        """Test building headers with required fields."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        await client.get("/test", cast_to=dict)

        request = httpx_mock.get_request()
        assert request is not None
        assert request.headers["x-client-id"] == CLIENT_ID
        assert request.headers["x-api-key"] == API_KEY
        assert request.headers["content-type"] == "application/json"
        assert "AsyncPayOS" in request.headers["user-agent"]

    @pytest.mark.asyncio
    async def test_build_headers_with_partner_code(self, httpx_mock: HTTPXMock):
        """Test headers include partner code when set."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
            partner_code=PARTNER_CODE,
        )

        await client.get("/test", cast_to=dict)

        request = httpx_mock.get_request()
        assert request is not None
        assert request.headers["x-partner-code"] == PARTNER_CODE

    @pytest.mark.asyncio
    async def test_build_headers_without_partner_code(self, httpx_mock: HTTPXMock):
        """Test headers don't include partner code when not set."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        await client.get("/test", cast_to=dict)

        request = httpx_mock.get_request()
        assert request is not None
        assert "x-partner-code" not in request.headers

    @pytest.mark.asyncio
    async def test_build_headers_with_custom_headers(self, httpx_mock: HTTPXMock):
        """Test merging custom headers."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        await client.get("/test", cast_to=dict, headers={"x-custom": "custom-value"})

        request = httpx_mock.get_request()
        assert request is not None
        assert request.headers["x-custom"] == "custom-value"
        assert request.headers["x-client-id"] == CLIENT_ID


class TestAsyncPayOSUrl:
    """Test URL building."""

    @pytest.mark.asyncio
    async def test_build_url_from_path(self, httpx_mock: HTTPXMock):
        """Test building URL from path."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/v2/payment-requests",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        await client.get("/v2/payment-requests", cast_to=dict)

        request = httpx_mock.get_request()
        assert request is not None
        assert str(request.url) == f"{BASE_URL}/v2/payment-requests"

    @pytest.mark.asyncio
    async def test_build_url_with_query_parameters(self, httpx_mock: HTTPXMock):
        """Test building URL with query parameters."""
        httpx_mock.add_response(
            method="GET",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        await client.get("/v1/payouts", cast_to=dict, query={"limit": 10, "offset": 0})

        request = httpx_mock.get_request()
        assert request is not None
        assert "limit=10" in str(request.url)
        assert "offset=0" in str(request.url)

    @pytest.mark.asyncio
    async def test_build_url_with_string_query_params(self, httpx_mock: HTTPXMock):
        """Test handling string query parameter values."""
        httpx_mock.add_response(
            method="GET",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        await client.get(
            "/v1/payouts", cast_to=dict, query={"filter": "SUCCEEDED", "status": "PROCESSING"}
        )

        request = httpx_mock.get_request()
        assert request is not None
        assert "filter=SUCCEEDED" in str(request.url)
        assert "status=PROCESSING" in str(request.url)

    @pytest.mark.asyncio
    async def test_build_url_with_array_query_params(self, httpx_mock: HTTPXMock):
        """Test handling array query parameters as JSON."""
        httpx_mock.add_response(
            method="GET",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        await client.get("/v1/payouts", cast_to=dict, query={"ids": ["id1", "id2", "id3"]})

        request = httpx_mock.get_request()
        assert request is not None
        url_str = str(request.url)
        assert "ids=" in url_str
        assert "id1" in url_str

    @pytest.mark.asyncio
    async def test_build_url_with_dict_query_params(self, httpx_mock: HTTPXMock):
        """Test handling object query parameters as JSON."""
        httpx_mock.add_response(
            method="GET",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        await client.get("/v1/payouts", cast_to=dict, query={"filter": {"status": "SUCCEEDED"}})

        request = httpx_mock.get_request()
        assert request is not None
        url_str = str(request.url)
        assert "filter=" in url_str
        assert "status" in url_str

    @pytest.mark.asyncio
    async def test_build_url_skips_none_query_params(self, httpx_mock: HTTPXMock):
        """Test that None query parameters are excluded."""
        httpx_mock.add_response(
            method="GET",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        await client.get(
            "/v1/payouts", cast_to=dict, query={"limit": 10, "offset": None, "status": "SUCCEEDED"}
        )

        request = httpx_mock.get_request()
        assert request is not None
        url_str = str(request.url)
        assert "offset" not in url_str
        assert "limit=10" in url_str
        assert "status=SUCCEEDED" in url_str

    @pytest.mark.asyncio
    async def test_build_url_with_empty_query_dict(self, httpx_mock: HTTPXMock):
        """Test handling empty query object."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/v2/payment-requests",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        await client.get("/v2/payment-requests", cast_to=dict, query={})

        request = httpx_mock.get_request()
        assert request is not None
        assert str(request.url) == f"{BASE_URL}/v2/payment-requests"


class TestAsyncPayOSBody:
    """Test body serialization."""

    @pytest.mark.asyncio
    async def test_build_body_with_dict(self, httpx_mock: HTTPXMock):
        """Test serializing dict to JSON string."""
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        await client.post("/test", cast_to=dict, body={"orderCode": 123, "amount": 50000})

        request = httpx_mock.get_request()
        assert request is not None
        assert b'"orderCode":123' in request.content or b'"orderCode": 123' in request.content
        assert b'"amount":50000' in request.content or b'"amount": 50000' in request.content

    @pytest.mark.asyncio
    async def test_build_body_with_string(self, httpx_mock: HTTPXMock):
        """Test string body is returned as is."""
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        await client.post("/test", cast_to=dict, body="test string")

        request = httpx_mock.get_request()
        assert request is not None
        assert request.content == b"test string"

    @pytest.mark.asyncio
    async def test_build_body_with_none(self, httpx_mock: HTTPXMock):
        """Test None body returns None."""
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        await client.post("/test", cast_to=dict, body=None)

        request = httpx_mock.get_request()
        assert request is not None
        assert request.content == b""

    @pytest.mark.asyncio
    async def test_build_body_with_bytes(self, httpx_mock: HTTPXMock):
        """Test bytes body is returned as is."""
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        await client.post("/test", cast_to=dict, body=b"test bytes")

        request = httpx_mock.get_request()
        assert request is not None
        assert request.content == b"test bytes"


class TestAsyncPayOSHttpMethods:
    """Test HTTP methods."""

    @pytest.mark.asyncio
    async def test_get_request(self, httpx_mock: HTTPXMock):
        """Test GET request."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {"result": "success"}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        result = await client.get("/test", cast_to=dict)

        assert result["result"] == "success"
        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "GET"

    @pytest.mark.asyncio
    async def test_post_request(self, httpx_mock: HTTPXMock):
        """Test POST request."""
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {"id": "123"}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        result = await client.post("/test", cast_to=dict, body={"field": "value"})

        assert result["id"] == "123"
        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "POST"

    @pytest.mark.asyncio
    async def test_patch_request(self, httpx_mock: HTTPXMock):
        """Test PATCH request."""
        httpx_mock.add_response(
            method="PATCH",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {"updated": True}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        result = await client.patch("/test", cast_to=dict, body={"field": "new_value"})

        assert result["updated"] is True
        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "PATCH"

    @pytest.mark.asyncio
    async def test_put_request(self, httpx_mock: HTTPXMock):
        """Test PUT request."""
        httpx_mock.add_response(
            method="PUT",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {"replaced": True}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        result = await client.put("/test", cast_to=dict, body={"field": "value"})

        assert result["replaced"] is True
        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "PUT"

    @pytest.mark.asyncio
    async def test_delete_request(self, httpx_mock: HTTPXMock):
        """Test DELETE request."""
        httpx_mock.add_response(
            method="DELETE",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {"deleted": True}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        result = await client.delete("/test", cast_to=dict)

        assert result["deleted"] is True
        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "DELETE"

    @pytest.mark.asyncio
    async def test_request_with_custom_headers(self, httpx_mock: HTTPXMock):
        """Test request with custom headers."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        await client.get("/test", cast_to=dict, headers={"x-custom-header": "custom-value"})

        request = httpx_mock.get_request()
        assert request is not None
        assert request.headers["x-custom-header"] == "custom-value"

    @pytest.mark.asyncio
    async def test_download_file(self, httpx_mock: HTTPXMock):
        """Test downloading file."""
        file_content = b"test file content"
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/files/test.txt",
            content=file_content,
            headers={
                "content-type": "text/plain",
                "content-disposition": 'attachment; filename="test.txt"',
            },
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        result = await client.download("/files/test.txt")

        assert result.data == file_content
        assert result.filename == "test.txt"
        assert result.content_type == "text/plain"
        assert result.size == len(file_content)


class TestAsyncPayOSRetryAndTimeout:
    """Test retry and timeout logic."""

    @pytest.mark.asyncio
    async def test_retry_on_500_error(self, httpx_mock: HTTPXMock):
        """Test retry on 500 Internal Server Error."""
        # First request fails with 500
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            status_code=500,
        )
        # Second request succeeds
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {"result": "success"}},
            status_code=200,
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
            max_retries=2,
        )

        result = await client.get("/test", cast_to=dict)

        assert result["result"] == "success"
        assert len(httpx_mock.get_requests()) == 2

    @pytest.mark.asyncio
    async def test_retry_on_429_rate_limit(self, httpx_mock: HTTPXMock):
        """Test retry on 429 Too Many Requests."""
        # First request fails with 429
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            status_code=429,
        )
        # Second request succeeds
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {"result": "success"}},
            status_code=200,
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
            max_retries=2,
        )

        result = await client.get("/test", cast_to=dict)

        assert result["result"] == "success"
        assert len(httpx_mock.get_requests()) == 2

    @pytest.mark.asyncio
    async def test_retry_on_408_timeout(self, httpx_mock: HTTPXMock):
        """Test retry on 408 Request Timeout."""
        # First request fails with 408
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            status_code=408,
        )
        # Second request succeeds
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {"result": "success"}},
            status_code=200,
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
            max_retries=2,
        )

        result = await client.get("/test", cast_to=dict)

        assert result["result"] == "success"
        assert len(httpx_mock.get_requests()) == 2

    @pytest.mark.asyncio
    async def test_no_retry_on_4xx_errors(self, httpx_mock: HTTPXMock):
        """Test no retry on 4xx errors (except 408, 429)."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "400", "desc": "Bad request"},
            status_code=400,
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
            max_retries=2,
        )

        with pytest.raises(BadRequestError):
            await client.get("/test", cast_to=dict)

        # Should only attempt once (no retries)
        assert len(httpx_mock.get_requests()) == 1

    @pytest.mark.asyncio
    async def test_max_retries_respected(self, httpx_mock: HTTPXMock):
        """Test that max_retries is respected."""
        # All requests fail with 500
        for _ in range(3):
            httpx_mock.add_response(
                method="GET",
                url=f"{BASE_URL}/test",
                status_code=500,
            )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
            max_retries=2,
        )

        with pytest.raises(InternalServerError):
            await client.get("/test", cast_to=dict)

        assert len(httpx_mock.get_requests()) == 3

    @pytest.mark.asyncio
    async def test_honor_retry_after_header(self, httpx_mock: HTTPXMock):
        """Test honoring Retry-After header."""
        # First request fails with 429 and Retry-After header
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            status_code=429,
            headers={"retry-after": "1"},
        )
        # Second request succeeds
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {"result": "success"}},
            status_code=200,
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
            max_retries=2,
        )

        result = await client.get("/test", cast_to=dict)

        assert result["result"] == "success"
        assert len(httpx_mock.get_requests()) == 2

    @pytest.mark.asyncio
    async def test_custom_max_retries(self, httpx_mock: HTTPXMock):
        """Test custom max_retries configuration."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            status_code=500,
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
            max_retries=0,
        )

        with pytest.raises(InternalServerError):
            await client.get("/test", cast_to=dict)

        # Should only attempt once (no retries)
        assert len(httpx_mock.get_requests()) == 1


class TestAsyncPayOSSignature:
    """Test signature verification."""

    @pytest.mark.asyncio
    async def test_verify_response_signature_from_header(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test verifying response signature from x-signature header."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {"field": "value"}},
            headers={"x-signature": "valid-signature"},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_async)
        mock_crypto_async.create_signature.return_value = "valid-signature"

        result = await client.get("/test", cast_to=dict, signature_response="header")

        mock_crypto_async.create_signature.assert_called_once()
        assert result["field"] == "value"

    @pytest.mark.asyncio
    async def test_verify_response_signature_from_body(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test verifying response signature from body."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={
                "code": "00",
                "desc": "success",
                "data": {"field": "value"},
                "signature": "valid-signature",
            },
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_async)
        mock_crypto_async.create_signature_from_object.return_value = "valid-signature"

        result = await client.get("/test", cast_to=dict, signature_response="body")

        mock_crypto_async.create_signature_from_object.assert_called_once()
        assert result["field"] == "value"

    @pytest.mark.asyncio
    async def test_signature_mismatch_raises_error(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test signature mismatch raises InvalidSignatureError."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {"field": "value"}},
            headers={"x-signature": "invalid-signature"},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_async)
        mock_crypto_async.create_signature.return_value = "valid-signature"

        with pytest.raises(InvalidSignatureError):
            await client.get("/test", cast_to=dict, signature_response="header")

    @pytest.mark.asyncio
    async def test_missing_signature_raises_error(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test missing signature raises InvalidSignatureError."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {"field": "value"}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_async)

        with pytest.raises(InvalidSignatureError, match="Missing response signature"):
            await client.get("/test", cast_to=dict, signature_response="header")

    @pytest.mark.asyncio
    async def test_missing_header_response_signature_on_success(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test success response without header signature raises InvalidSignatureError."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {"field": "value"}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_async)

        with pytest.raises(InvalidSignatureError, match="Missing response signature"):
            await client.get("/test", cast_to=dict, signature_response="header")

    @pytest.mark.asyncio
    async def test_missing_body_response_signature_on_success(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test success response without body signature raises InvalidSignatureError."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {"field": "value"}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_async)

        with pytest.raises(InvalidSignatureError, match="Missing response signature"):
            await client.get("/test", cast_to=dict, signature_response="body")

    @pytest.mark.asyncio
    async def test_unencodable_body_response_signature_fails_verification(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test lone-surrogate body signature raises InvalidSignatureError."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            content=b'{"code": "00", "desc": "success", "data": {}, "signature": "\\ud800"}',
            headers={"content-type": "application/json"},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_async)

        with pytest.raises(InvalidSignatureError, match="Response signature verification failed"):
            await client.get("/test", cast_to=dict, signature_response="body")

    @pytest.mark.asyncio
    async def test_sign_request_with_body_signature(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test signing request with body signature type."""
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_async)
        mock_crypto_async.create_signature_from_object.return_value = "request-signature"

        await client.post("/test", cast_to=dict, body={"field": "value"}, signature_request="body")

        mock_crypto_async.create_signature_from_object.assert_called_once()

    @pytest.mark.asyncio
    async def test_sign_request_with_header_signature(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test signing request with header signature type."""
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_async)
        mock_crypto_async.create_signature.return_value = "request-signature"

        await client.post(
            "/test", cast_to=dict, body={"field": "value"}, signature_request="header"
        )

        mock_crypto_async.create_signature.assert_called_once()
        request = httpx_mock.get_request()
        assert request is not None
        assert request.headers["x-signature"] == "request-signature"


class TestAsyncPayOSErrors:
    """Test error classes."""

    def test_payos_error_accessible(self):
        """Test PayOSError is accessible."""
        from payos import PayOSError as ImportedError

        assert ImportedError is not None

    def test_api_error_accessible(self):
        """Test APIError is accessible."""
        from payos import APIError as ImportedError

        assert ImportedError is not None

    def test_bad_request_error_accessible(self):
        """Test BadRequestError is accessible."""
        from payos import BadRequestError as ImportedError

        assert ImportedError is not None

    def test_unauthorized_error_accessible(self):
        """Test UnauthorizedError is accessible."""
        from payos import UnauthorizedError as ImportedError

        assert ImportedError is not None

    def test_forbidden_error_accessible(self):
        """Test ForbiddenError is accessible."""
        from payos import ForbiddenError as ImportedError

        assert ImportedError is not None

    def test_not_found_error_accessible(self):
        """Test NotFoundError is accessible."""
        from payos import NotFoundError as ImportedError

        assert ImportedError is not None

    def test_too_many_requests_error_accessible(self):
        """Test TooManyRequestsError is accessible."""
        from payos import TooManyRequestsError as ImportedError

        assert ImportedError is not None

    def test_internal_server_error_accessible(self):
        """Test InternalServerError is accessible."""
        from payos import InternalServerError as ImportedError

        assert ImportedError is not None

    def test_connection_error_accessible(self):
        """Test ConnectionError is accessible."""
        from payos import ConnectionError as ImportedError

        assert ImportedError is not None

    def test_connection_timeout_error_accessible(self):
        """Test ConnectionTimeoutError is accessible."""
        from payos import ConnectionTimeoutError as ImportedError

        assert ImportedError is not None

    def test_invalid_signature_error_accessible(self):
        """Test InvalidSignatureError is accessible."""
        from payos import InvalidSignatureError as ImportedError

        assert ImportedError is not None

    def test_webhook_error_accessible(self):
        """Test WebhookError is accessible."""
        from payos import WebhookError as ImportedError

        assert ImportedError is not None

    @pytest.mark.asyncio
    async def test_bad_request_error_raised(self, httpx_mock: HTTPXMock):
        """Test BadRequestError is raised on 400 status."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "400", "desc": "Bad request"},
            status_code=400,
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        with pytest.raises(BadRequestError) as exc_info:
            await client.get("/test", cast_to=dict)

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_unauthorized_error_raised(self, httpx_mock: HTTPXMock):
        """Test UnauthorizedError is raised on 401 status."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "401", "desc": "Unauthorized"},
            status_code=401,
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        with pytest.raises(UnauthorizedError) as exc_info:
            await client.get("/test", cast_to=dict)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_not_found_error_raised(self, httpx_mock: HTTPXMock):
        """Test NotFoundError is raised on 404 status."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "404", "desc": "Not found"},
            status_code=404,
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        with pytest.raises(NotFoundError) as exc_info:
            await client.get("/test", cast_to=dict)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_api_error_on_non_00_code(self, httpx_mock: HTTPXMock):
        """Test APIError is raised when response code is not '00'."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "999", "desc": "Custom error"},
            status_code=200,
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        with pytest.raises(APIError) as exc_info:
            await client.get("/test", cast_to=dict)

        assert exc_info.value.error_code == "999"


class TestAsyncPayOSRedirects:
    """Test redirects followed by a custom http_client with follow_redirects=True."""

    def _client(self) -> AsyncPayOS:
        return AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
            max_retries=0,
            http_client=httpx.AsyncClient(follow_redirects=True),
        )

    @pytest.mark.asyncio
    async def test_cross_origin_redirect_drops_credentials(self, httpx_mock: HTTPXMock):
        """Test credentials are not forwarded to another origin."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            status_code=302,
            headers={"location": "https://other.example/landed"},
        )
        httpx_mock.add_response(
            method="GET",
            url="https://other.example/landed",
            json={"code": "00", "desc": "success", "data": {}},
        )

        await self._client().get("/test", cast_to=dict)

        redirected = httpx_mock.get_requests()[-1]
        assert "x-api-key" not in redirected.headers
        assert "x-client-id" not in redirected.headers

    @pytest.mark.asyncio
    async def test_same_origin_redirect_keeps_credentials(self, httpx_mock: HTTPXMock):
        """Test credentials are kept on a same-origin redirect."""
        httpx_mock.add_response(
            method="GET", url=f"{BASE_URL}/test", status_code=302, headers={"location": "/landed"}
        )
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/landed",
            json={"code": "00", "desc": "success", "data": {}},
        )

        await self._client().get("/test", cast_to=dict)

        redirected = httpx_mock.get_requests()[-1]
        assert redirected.headers["x-api-key"] == API_KEY
        assert redirected.headers["x-client-id"] == CLIENT_ID

    CREDENTIAL_HEADERS = (
        "x-api-key",
        "x-client-id",
        "x-partner-code",
        "authorization",
        "cookie",
        "proxy-authorization",
    )
    EXTRA_HEADERS = {
        "authorization": "Bearer test-token",
        "cookie": "session=test-cookie",
        "proxy-authorization": "Basic dGVzdDp0ZXN0",
    }

    def _partner_client(self, http_client: httpx.AsyncClient) -> AsyncPayOS:
        return AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            partner_code=PARTNER_CODE,
            base_url=BASE_URL,
            max_retries=0,
            http_client=http_client,
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "target",
        [
            "https://other.example/landed",
            "https://api-test.payos.vn:8443/landed",
            "http://api-test.payos.vn/landed",
        ],
        ids=["other host", "other port", "other scheme"],
    )
    async def test_cross_origin_redirect_removes_credential_headers(
        self, httpx_mock: HTTPXMock, target: str
    ):
        """Test every credential header, including the partner code, is removed on a cross-origin hop."""
        httpx_mock.add_response(
            method="GET", url=f"{BASE_URL}/test", status_code=302, headers={"location": target}
        )
        httpx_mock.add_response(
            method="GET", url=target, json={"code": "00", "desc": "success", "data": {}}
        )

        await self._partner_client(httpx.AsyncClient(follow_redirects=True)).get(
            "/test", headers=dict(self.EXTRA_HEADERS), cast_to=dict
        )

        first, redirected = httpx_mock.get_requests()
        assert first.headers["x-partner-code"] == PARTNER_CODE
        for name in self.CREDENTIAL_HEADERS:
            assert name in first.headers
            assert name not in redirected.headers
        assert str(redirected.url) == target

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "location", ["/landed", "https://api-test.payos.vn:443/landed"], ids=["relative", "port"]
    )
    async def test_same_origin_redirect_keeps_credential_headers(
        self, httpx_mock: HTTPXMock, location: str
    ):
        """Test every credential header, including the partner code, is kept on a same-origin hop."""
        httpx_mock.add_response(
            method="GET", url=f"{BASE_URL}/test", status_code=302, headers={"location": location}
        )
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/landed",
            json={"code": "00", "desc": "success", "data": {}},
        )

        await self._partner_client(httpx.AsyncClient(follow_redirects=True)).get(
            "/test", headers=dict(self.EXTRA_HEADERS), cast_to=dict
        )

        first, redirected = httpx_mock.get_requests()
        for name in self.CREDENTIAL_HEADERS:
            if name != "cookie":
                assert redirected.headers[name] == first.headers[name]
        assert redirected.headers["x-partner-code"] == PARTNER_CODE
        # Like httpx, the Cookie header is rebuilt from the client cookie jar on each hop.
        assert "cookie" not in redirected.headers

    @pytest.mark.asyncio
    async def test_credential_headers_stay_removed_after_returning_to_origin(
        self, httpx_mock: HTTPXMock
    ):
        """Test headers removed on a cross-origin hop are not restored when the chain returns."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            status_code=302,
            headers={"location": "https://other.example/hop"},
        )
        httpx_mock.add_response(
            method="GET",
            url="https://other.example/hop",
            status_code=302,
            headers={"location": f"{BASE_URL}/landed"},
        )
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/landed",
            json={"code": "00", "desc": "success", "data": {}},
        )

        await self._partner_client(httpx.AsyncClient(follow_redirects=True)).get(
            "/test", headers=dict(self.EXTRA_HEADERS), cast_to=dict
        )

        requests = httpx_mock.get_requests()
        assert [str(request.url) for request in requests] == [
            f"{BASE_URL}/test",
            "https://other.example/hop",
            f"{BASE_URL}/landed",
        ]
        for request in requests[1:]:
            for name in self.CREDENTIAL_HEADERS:
                assert name not in request.headers

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("status_code", "method", "expected_method"),
        [
            (303, "POST", "GET"),
            (303, "PUT", "GET"),
            (301, "POST", "GET"),
            (302, "POST", "GET"),
            (302, "PUT", "PUT"),
            (307, "POST", "POST"),
            (307, "PUT", "PUT"),
            (308, "POST", "POST"),
        ],
    )
    async def test_redirect_method_and_body(
        self, httpx_mock: HTTPXMock, status_code: int, method: str, expected_method: str
    ):
        """Test 303 and 301/302 answering POST switch to GET without body; others keep both."""
        httpx_mock.add_response(
            method=method,
            url=f"{BASE_URL}/test",
            status_code=status_code,
            headers={"location": "/landed"},
        )
        httpx_mock.add_response(
            method=expected_method,
            url=f"{BASE_URL}/landed",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = self._partner_client(httpx.AsyncClient(follow_redirects=True))
        send = client.post if method == "POST" else client.put
        await send("/test", body={"amount": 2000}, cast_to=dict)

        first, redirected = httpx_mock.get_requests()
        assert redirected.method == expected_method
        if expected_method == "GET":
            assert redirected.content == b""
            assert "content-type" not in redirected.headers
            assert "content-length" not in redirected.headers
        else:
            assert redirected.content == first.content
            assert redirected.headers["content-type"] == "application/json"

    @pytest.mark.asyncio
    async def test_five_redirects_are_followed(self, httpx_mock: HTTPXMock):
        """Test a chain of exactly five redirects is followed."""
        for hop in range(5):
            httpx_mock.add_response(
                method="GET",
                url=f"{BASE_URL}/hop{hop}",
                status_code=302,
                headers={"location": f"/hop{hop + 1}"},
            )
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/hop5",
            json={"code": "00", "desc": "success", "data": {"ok": True}},
        )

        result = await self._partner_client(httpx.AsyncClient(follow_redirects=True)).get(
            "/hop0", cast_to=dict
        )

        assert result == {"ok": True}
        assert len(httpx_mock.get_requests()) == 6

    @pytest.mark.asyncio
    async def test_sixth_redirect_fails(self, httpx_mock: HTTPXMock):
        """Test a sixth redirect raises before it is followed."""
        for hop in range(6):
            httpx_mock.add_response(
                method="GET",
                url=f"{BASE_URL}/hop{hop}",
                status_code=302,
                headers={"location": f"/hop{hop + 1}"},
            )

        with pytest.raises(PayOSError) as excinfo:
            await self._partner_client(httpx.AsyncClient(follow_redirects=True)).get(
                "/hop0", cast_to=dict
            )

        assert type(excinfo.value) is PayOSError
        assert str(excinfo.value) == "Too many redirects (more than 5)"
        assert len(httpx_mock.get_requests()) == 6

    @pytest.mark.asyncio
    @pytest.mark.parametrize("custom", [True, False], ids=["custom client", "default client"])
    async def test_client_without_follow_redirects_does_not_follow(
        self, httpx_mock: HTTPXMock, custom: bool
    ):
        """Test a redirect is returned as an error when the http client does not follow redirects."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            status_code=302,
            headers={"location": "https://other.example/landed"},
            json={"code": "302", "desc": "Found"},
        )

        client = (
            self._partner_client(httpx.AsyncClient())
            if custom
            else AsyncPayOS(
                client_id=CLIENT_ID,
                api_key=API_KEY,
                checksum_key=CHECKSUM_KEY,
                partner_code=PARTNER_CODE,
                base_url=BASE_URL,
                max_retries=0,
            )
        )
        with pytest.raises(APIError) as excinfo:
            await client.get("/test", cast_to=dict)

        assert excinfo.value.status_code == 302
        assert len(httpx_mock.get_requests()) == 1


class TestAsyncPayOSConstants:
    """Test static constants."""

    def test_default_base_url(self):
        """Test DEFAULT_BASE_URL constant."""
        assert DEFAULT_BASE_URL == "https://api-merchant.payos.vn"

    def test_default_timeout(self):
        """Test DEFAULT_TIMEOUT constant."""
        assert DEFAULT_TIMEOUT == 60.0

    def test_default_max_retries(self):
        """Test DEFAULT_MAX_RETRIES constant."""
        assert DEFAULT_MAX_RETRIES == 2


class TestAsyncPayOSRedirectChain:
    """Test auth, cookies and statuses across a manually followed redirect chain."""

    OK = {"code": "00", "desc": "success", "data": {}}

    def _client(self, **kwargs: Any) -> AsyncPayOS:
        return AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
            http_client=httpx.AsyncClient(follow_redirects=True, **kwargs),
        )

    @pytest.mark.asyncio
    async def test_client_auth_only_on_original_origin(self, httpx_mock: HTTPXMock):
        """Test client auth is kept on a same-origin hop and not re-applied after leaving the origin."""
        httpx_mock.add_response(url=f"{BASE_URL}/a", status_code=302, headers={"location": "/b"})
        httpx_mock.add_response(
            url=f"{BASE_URL}/b",
            status_code=302,
            headers={"location": "https://u:p@other.example/c"},
        )
        httpx_mock.add_response(url="https://other.example/c", json=self.OK)

        await self._client(auth=("u", "p")).get("/a", cast_to=dict)

        first, same, other = httpx_mock.get_requests()
        assert same.headers["authorization"] == first.headers["authorization"]
        assert "authorization" not in other.headers

    @pytest.mark.asyncio
    async def test_client_auth_is_recomputed_for_same_origin_hop(self, httpx_mock: HTTPXMock):
        """Test client auth that depends on the URL is applied again for a same-origin hop."""

        class PathAuth(httpx.Auth):
            def auth_flow(self, request: httpx.Request) -> Any:
                request.headers["authorization"] = f"path {request.url.path}"
                yield request

        httpx_mock.add_response(url=f"{BASE_URL}/a", status_code=302, headers={"location": "/b"})
        httpx_mock.add_response(url=f"{BASE_URL}/b", json=self.OK)

        await self._client(auth=PathAuth()).get("/a", cast_to=dict)

        assert httpx_mock.get_requests()[-1].headers["authorization"] == "path /b"

    @pytest.mark.asyncio
    async def test_same_origin_set_cookie_on_redirect_is_sent(self, httpx_mock: HTTPXMock):
        """Test a cookie set by a same-origin redirect is sent on the next same-origin hop."""
        httpx_mock.add_response(
            url=f"{BASE_URL}/a",
            status_code=302,
            headers={"location": "/b", "set-cookie": "sid=1; Path=/"},
        )
        httpx_mock.add_response(url=f"{BASE_URL}/b", json=self.OK)

        await self._client().get("/a", cast_to=dict)

        assert httpx_mock.get_requests()[-1].headers["cookie"] == "sid=1"

    @pytest.mark.asyncio
    async def test_cookies_never_sent_after_leaving_origin(self, httpx_mock: HTTPXMock):
        """Test jar cookies are not added again on B to B or back on A after leaving the origin."""
        other = "https://other.example"
        httpx_mock.add_response(
            url=f"{BASE_URL}/a", status_code=302, headers={"location": f"{other}/b1"}
        )
        httpx_mock.add_response(
            url=f"{other}/b1",
            status_code=302,
            headers={"location": "/b2", "set-cookie": "bsid=2; Path=/"},
        )
        httpx_mock.add_response(
            url=f"{other}/b2", status_code=302, headers={"location": f"{BASE_URL}/back"}
        )
        httpx_mock.add_response(url=f"{BASE_URL}/back", json=self.OK)

        client = self._client(cookies={"sid": "1"})
        await client.get("/a", cast_to=dict)

        first, *rest = httpx_mock.get_requests()
        assert first.headers["cookie"] == "sid=1"
        for request in rest:
            assert "cookie" not in request.headers
            assert "x-api-key" not in request.headers

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status", [300, 304, 305, 306, 399])
    async def test_non_redirect_3xx_is_not_followed(self, httpx_mock: HTTPXMock, status: int):
        """Test only 301/302/303/307/308 are followed."""
        httpx_mock.add_response(
            url=f"{BASE_URL}/a",
            status_code=status,
            headers={"location": "/b"},
            json={"code": str(status), "desc": "redirect"},
        )

        with pytest.raises(PayOSError):
            await self._client().get("/a", cast_to=dict)

        assert len(httpx_mock.get_requests()) == 1

    @pytest.mark.asyncio
    async def test_too_many_redirects_with_default_retries(self, httpx_mock: HTTPXMock):
        """Test exceeding the redirect cap is not retried."""
        httpx_mock.add_response(
            url=f"{BASE_URL}/a", status_code=302, headers={"location": "/a"}, is_reusable=True
        )

        with pytest.raises(PayOSError, match=r"Too many redirects \(more than 5\)"):
            await self._client().get("/a", cast_to=dict)

        assert len(httpx_mock.get_requests()) == 6
