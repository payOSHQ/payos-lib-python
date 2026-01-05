"""Tests for synchronous PayOS client."""

import pytest
from pytest_httpx import HTTPXMock

from payos import (
    PayOS,
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


class TestPayOSInitialization:
    """Test PayOS client initialization."""

    def test_create_client_with_valid_credentials(self):
        """Test creating client with valid credentials."""
        client = PayOS(
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
            PayOS(
                api_key=API_KEY,
                checksum_key=CHECKSUM_KEY,
            )

    def test_missing_api_key_raises_error(self):
        """Test that missing api_key raises PayOSError."""
        with pytest.raises(PayOSError, match="PAYOS_API_KEY"):
            PayOS(
                client_id=CLIENT_ID,
                checksum_key=CHECKSUM_KEY,
            )

    def test_missing_checksum_key_raises_error(self):
        """Test that missing checksum_key raises PayOSError."""
        with pytest.raises(PayOSError, match="PAYOS_CHECKSUM_KEY"):
            PayOS(
                client_id=CLIENT_ID,
                api_key=API_KEY,
            )

    def test_default_timeout_and_max_retries(self):
        """Test default timeout and max_retries values."""
        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
        )

        assert client.timeout == DEFAULT_TIMEOUT
        assert client.max_retries == DEFAULT_MAX_RETRIES

    def test_override_timeout_and_max_retries(self):
        """Test overriding timeout and max_retries."""
        client = PayOS(
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
        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
        )

        assert client.base_url == DEFAULT_BASE_URL

    def test_partner_code_when_provided(self):
        """Test partner code is set when provided."""
        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            partner_code=PARTNER_CODE,
        )

        assert client.partner_code == PARTNER_CODE

    def test_partner_code_when_not_provided(self):
        """Test partner code is None when not provided."""
        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
        )

        assert client.partner_code is None

    def test_resources_initialized(self):
        """Test that resource properties are accessible."""
        client = PayOS(
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
        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
        )

        assert "PayOS" in client.user_agent
        assert "Python" in client.user_agent

    def test_context_manager(self):
        """Test client can be used as context manager."""
        with PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
        ) as client:
            assert client is not None


class TestPayOSHeaders:
    """Test header building."""

    def test_build_headers_with_required_fields(self, httpx_mock: HTTPXMock):
        """Test building headers with required fields."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        client.get("/test", cast_to=dict)

        request = httpx_mock.get_request()
        assert request is not None
        assert request.headers["x-client-id"] == CLIENT_ID
        assert request.headers["x-api-key"] == API_KEY
        assert request.headers["content-type"] == "application/json"
        assert "PayOS" in request.headers["user-agent"]

    def test_build_headers_with_partner_code(self, httpx_mock: HTTPXMock):
        """Test headers include partner code when set."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
            partner_code=PARTNER_CODE,
        )

        client.get("/test", cast_to=dict)

        request = httpx_mock.get_request()
        assert request is not None
        assert request.headers["x-partner-code"] == PARTNER_CODE

    def test_build_headers_without_partner_code(self, httpx_mock: HTTPXMock):
        """Test headers don't include partner code when not set."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        client.get("/test", cast_to=dict)

        request = httpx_mock.get_request()
        assert request is not None
        assert "x-partner-code" not in request.headers

    def test_build_headers_with_custom_headers(self, httpx_mock: HTTPXMock):
        """Test merging custom headers."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        client.get("/test", cast_to=dict, headers={"x-custom": "custom-value"})

        request = httpx_mock.get_request()
        assert request is not None
        assert request.headers["x-custom"] == "custom-value"
        assert request.headers["x-client-id"] == CLIENT_ID


class TestPayOSUrl:
    """Test URL building."""

    def test_build_url_from_path(self, httpx_mock: HTTPXMock):
        """Test building URL from path."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/v2/payment-requests",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        client.get("/v2/payment-requests", cast_to=dict)

        request = httpx_mock.get_request()
        assert request is not None
        assert str(request.url) == f"{BASE_URL}/v2/payment-requests"

    def test_build_url_with_query_parameters(self, httpx_mock: HTTPXMock):
        """Test building URL with query parameters."""
        httpx_mock.add_response(
            method="GET",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        client.get("/v1/payouts", cast_to=dict, query={"limit": 10, "offset": 0})

        request = httpx_mock.get_request()
        assert request is not None
        assert "limit=10" in str(request.url)
        assert "offset=0" in str(request.url)

    def test_build_url_with_string_query_params(self, httpx_mock: HTTPXMock):
        """Test handling string query parameter values."""
        httpx_mock.add_response(
            method="GET",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        client.get(
            "/v1/payouts", cast_to=dict, query={"filter": "SUCCEEDED", "status": "PROCESSING"}
        )

        request = httpx_mock.get_request()
        assert request is not None
        assert "filter=SUCCEEDED" in str(request.url)
        assert "status=PROCESSING" in str(request.url)

    def test_build_url_with_array_query_params(self, httpx_mock: HTTPXMock):
        """Test handling array query parameters as JSON."""
        httpx_mock.add_response(
            method="GET",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        client.get("/v1/payouts", cast_to=dict, query={"ids": ["id1", "id2", "id3"]})

        request = httpx_mock.get_request()
        assert request is not None
        url_str = str(request.url)
        assert "ids=" in url_str
        assert "id1" in url_str

    def test_build_url_with_dict_query_params(self, httpx_mock: HTTPXMock):
        """Test handling object query parameters as JSON."""
        httpx_mock.add_response(
            method="GET",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        client.get("/v1/payouts", cast_to=dict, query={"filter": {"status": "SUCCEEDED"}})

        request = httpx_mock.get_request()
        assert request is not None
        url_str = str(request.url)
        assert "filter=" in url_str
        assert "status" in url_str

    def test_build_url_skips_none_query_params(self, httpx_mock: HTTPXMock):
        """Test that None query parameters are excluded."""
        httpx_mock.add_response(
            method="GET",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        client.get(
            "/v1/payouts", cast_to=dict, query={"limit": 10, "offset": None, "status": "SUCCEEDED"}
        )

        request = httpx_mock.get_request()
        assert request is not None
        url_str = str(request.url)
        assert "offset" not in url_str
        assert "limit=10" in url_str
        assert "status=SUCCEEDED" in url_str

    def test_build_url_with_empty_query_dict(self, httpx_mock: HTTPXMock):
        """Test handling empty query object."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/v2/payment-requests",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        client.get("/v2/payment-requests", cast_to=dict, query={})

        request = httpx_mock.get_request()
        assert request is not None
        assert str(request.url) == f"{BASE_URL}/v2/payment-requests"


class TestPayOSBody:
    """Test body serialization."""

    def test_build_body_with_dict(self, httpx_mock: HTTPXMock):
        """Test serializing dict to JSON string."""
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        client.post("/test", cast_to=dict, body={"orderCode": 123, "amount": 50000})

        request = httpx_mock.get_request()
        assert request is not None
        assert b'"orderCode":123' in request.content or b'"orderCode": 123' in request.content
        assert b'"amount":50000' in request.content or b'"amount": 50000' in request.content

    def test_build_body_with_string(self, httpx_mock: HTTPXMock):
        """Test string body is returned as is."""
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        client.post("/test", cast_to=dict, body="test string")

        request = httpx_mock.get_request()
        assert request is not None
        assert request.content == b"test string"

    def test_build_body_with_none(self, httpx_mock: HTTPXMock):
        """Test None body returns None."""
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        client.post("/test", cast_to=dict, body=None)

        request = httpx_mock.get_request()
        assert request is not None
        assert request.content == b""

    def test_build_body_with_bytes(self, httpx_mock: HTTPXMock):
        """Test bytes body is returned as is."""
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        client.post("/test", cast_to=dict, body=b"test bytes")

        request = httpx_mock.get_request()
        assert request is not None
        assert request.content == b"test bytes"


class TestPayOSHttpMethods:
    """Test HTTP methods."""

    def test_get_request(self, httpx_mock: HTTPXMock):
        """Test GET request."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {"result": "success"}},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        result = client.get("/test", cast_to=dict)

        assert result["result"] == "success"
        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "GET"

    def test_post_request(self, httpx_mock: HTTPXMock):
        """Test POST request."""
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {"id": "123"}},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        result = client.post("/test", cast_to=dict, body={"field": "value"})

        assert result["id"] == "123"
        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "POST"

    def test_patch_request(self, httpx_mock: HTTPXMock):
        """Test PATCH request."""
        httpx_mock.add_response(
            method="PATCH",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {"updated": True}},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        result = client.patch("/test", cast_to=dict, body={"field": "new_value"})

        assert result["updated"] is True
        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "PATCH"

    def test_put_request(self, httpx_mock: HTTPXMock):
        """Test PUT request."""
        httpx_mock.add_response(
            method="PUT",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {"replaced": True}},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        result = client.put("/test", cast_to=dict, body={"field": "value"})

        assert result["replaced"] is True
        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "PUT"

    def test_delete_request(self, httpx_mock: HTTPXMock):
        """Test DELETE request."""
        httpx_mock.add_response(
            method="DELETE",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {"deleted": True}},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        result = client.delete("/test", cast_to=dict)

        assert result["deleted"] is True
        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "DELETE"

    def test_request_with_custom_headers(self, httpx_mock: HTTPXMock):
        """Test request with custom headers."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        client.get("/test", cast_to=dict, headers={"x-custom-header": "custom-value"})

        request = httpx_mock.get_request()
        assert request is not None
        assert request.headers["x-custom-header"] == "custom-value"

    def test_download_file(self, httpx_mock: HTTPXMock):
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

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        result = client.download("/files/test.txt")

        assert result.data == file_content
        assert result.filename == "test.txt"
        assert result.content_type == "text/plain"
        assert result.size == len(file_content)


class TestPayOSRetryAndTimeout:
    """Test retry and timeout logic."""

    def test_retry_on_500_error(self, httpx_mock: HTTPXMock):
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

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
            max_retries=2,
        )

        result = client.get("/test", cast_to=dict)

        assert result["result"] == "success"
        assert len(httpx_mock.get_requests()) == 2

    def test_retry_on_429_rate_limit(self, httpx_mock: HTTPXMock):
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

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
            max_retries=2,
        )

        result = client.get("/test", cast_to=dict)

        assert result["result"] == "success"
        assert len(httpx_mock.get_requests()) == 2

    def test_retry_on_408_timeout(self, httpx_mock: HTTPXMock):
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

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
            max_retries=2,
        )

        result = client.get("/test", cast_to=dict)

        assert result["result"] == "success"
        assert len(httpx_mock.get_requests()) == 2

    def test_no_retry_on_4xx_errors(self, httpx_mock: HTTPXMock):
        """Test no retry on 4xx errors (except 408, 429)."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "400", "desc": "Bad request"},
            status_code=400,
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
            max_retries=2,
        )

        with pytest.raises(BadRequestError):
            client.get("/test", cast_to=dict)

        # Should only attempt once (no retries)
        assert len(httpx_mock.get_requests()) == 1

    def test_max_retries_respected(self, httpx_mock: HTTPXMock):
        """Test that max_retries is respected."""
        # All requests fail with 500
        for _ in range(3):
            httpx_mock.add_response(
                method="GET",
                url=f"{BASE_URL}/test",
                status_code=500,
            )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
            max_retries=2,
        )

        with pytest.raises(InternalServerError):
            client.get("/test", cast_to=dict)

        assert len(httpx_mock.get_requests()) == 3

    def test_honor_retry_after_header(self, httpx_mock: HTTPXMock):
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

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
            max_retries=2,
        )

        result = client.get("/test", cast_to=dict)

        assert result["result"] == "success"
        assert len(httpx_mock.get_requests()) == 2

    def test_custom_max_retries(self, httpx_mock: HTTPXMock):
        """Test custom max_retries configuration."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            status_code=500,
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
            max_retries=0,
        )

        with pytest.raises(InternalServerError):
            client.get("/test", cast_to=dict)

        # Should only attempt once (no retries)
        assert len(httpx_mock.get_requests()) == 1


class TestPayOSSignature:
    """Test signature verification."""

    def test_verify_response_signature_from_header(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test verifying response signature from x-signature header."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {"field": "value"}},
            headers={"x-signature": "valid-signature"},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_sync)
        mock_crypto_sync.create_signature.return_value = "valid-signature"

        result = client.get("/test", cast_to=dict, signature_response="header")

        mock_crypto_sync.create_signature.assert_called_once()
        assert result["field"] == "value"

    def test_verify_response_signature_from_body(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
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

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_sync)
        mock_crypto_sync.create_signature_from_object.return_value = "valid-signature"

        result = client.get("/test", cast_to=dict, signature_response="body")

        mock_crypto_sync.create_signature_from_object.assert_called_once()
        assert result["field"] == "value"

    def test_signature_mismatch_raises_error(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test signature mismatch raises InvalidSignatureError."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {"field": "value"}},
            headers={"x-signature": "invalid-signature"},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_sync)
        mock_crypto_sync.create_signature.return_value = "valid-signature"

        with pytest.raises(InvalidSignatureError):
            client.get("/test", cast_to=dict, signature_response="header")

    def test_missing_signature_raises_error(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test missing signature raises InvalidSignatureError."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {"field": "value"}},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_sync)

        with pytest.raises(InvalidSignatureError, match="signature missing"):
            client.get("/test", cast_to=dict, signature_response="header")

    def test_sign_request_with_body_signature(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test signing request with body signature type."""
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_sync)
        mock_crypto_sync.create_signature_from_object.return_value = "request-signature"

        client.post("/test", cast_to=dict, body={"field": "value"}, signature_request="body")

        mock_crypto_sync.create_signature_from_object.assert_called_once()

    def test_sign_request_with_header_signature(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test signing request with header signature type."""
        httpx_mock.add_response(
            method="POST",
            url=f"{BASE_URL}/test",
            json={"code": "00", "desc": "success", "data": {}},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_sync)
        mock_crypto_sync.create_signature.return_value = "request-signature"

        client.post("/test", cast_to=dict, body={"field": "value"}, signature_request="header")

        mock_crypto_sync.create_signature.assert_called_once()
        request = httpx_mock.get_request()
        assert request is not None
        assert request.headers["x-signature"] == "request-signature"


class TestPayOSErrors:
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

    def test_bad_request_error_raised(self, httpx_mock: HTTPXMock):
        """Test BadRequestError is raised on 400 status."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "400", "desc": "Bad request"},
            status_code=400,
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        with pytest.raises(BadRequestError) as exc_info:
            client.get("/test", cast_to=dict)

        assert exc_info.value.status_code == 400

    def test_unauthorized_error_raised(self, httpx_mock: HTTPXMock):
        """Test UnauthorizedError is raised on 401 status."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "401", "desc": "Unauthorized"},
            status_code=401,
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        with pytest.raises(UnauthorizedError) as exc_info:
            client.get("/test", cast_to=dict)

        assert exc_info.value.status_code == 401

    def test_not_found_error_raised(self, httpx_mock: HTTPXMock):
        """Test NotFoundError is raised on 404 status."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "404", "desc": "Not found"},
            status_code=404,
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        with pytest.raises(NotFoundError) as exc_info:
            client.get("/test", cast_to=dict)

        assert exc_info.value.status_code == 404

    def test_api_error_on_non_00_code(self, httpx_mock: HTTPXMock):
        """Test APIError is raised when response code is not '00'."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/test",
            json={"code": "999", "desc": "Custom error"},
            status_code=200,
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        with pytest.raises(APIError) as exc_info:
            client.get("/test", cast_to=dict)

        assert exc_info.value.error_code == "999"


class TestPayOSConstants:
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
