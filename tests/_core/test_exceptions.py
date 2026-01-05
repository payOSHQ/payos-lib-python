"""Tests for core exceptions."""

import httpx
import pytest

from payos import (
    APIError,
    BadRequestError,
    ConnectionError,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
    PayOSError,
    TooManyRequestsError,
    UnauthorizedError,
    WebhookError,
)


class TestPayOSError:
    """Test PayOSError base exception."""

    def test_payos_error_creation(self):
        """Test creating PayOSError with message."""
        error = PayOSError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    def test_payos_error_inheritance(self):
        """Test that other errors inherit from PayOSError."""
        api_error = APIError("API error")
        connection_error = ConnectionError("Connection error")
        webhook_error = WebhookError("Webhook error")

        assert isinstance(api_error, PayOSError)
        assert isinstance(connection_error, PayOSError)
        assert isinstance(webhook_error, PayOSError)


class TestAPIError:
    """Test APIError and its factory method."""

    def test_api_error_creation_with_all_fields(self):
        """Test creating APIError with all fields."""
        response = httpx.Response(400, request=httpx.Request("GET", "http://test"))
        error = APIError(
            "Error message",
            status_code=400,
            error_code="ERR001",
            error_desc="Bad request description",
            response=response,
        )

        assert str(error) == "Error message"
        assert error.status_code == 400
        assert error.error_code == "ERR001"
        assert error.error_desc == "Bad request description"
        assert error.response == response

    def test_api_error_message_contains_code_and_desc(self):
        """Test that error message contains code and desc when present."""
        error_data = {"code": "X", "desc": "desc"}
        response = httpx.Response(
            400,
            json=error_data,
            request=httpx.Request("GET", "http://test"),
        )

        error = APIError.from_response(response, error_data=error_data, message="API Error")

        # The message is custom provided
        assert str(error) == "API Error"
        assert error.error_code == "X"
        assert error.error_desc == "desc"

    def test_from_response_returns_bad_request_error_for_400(self):
        """Test that from_response returns BadRequestError for 400 status."""
        response = httpx.Response(
            400,
            json={"code": "c", "desc": "d"},
            request=httpx.Request("GET", "http://test"),
        )
        error = APIError.from_response(response, error_data={"code": "c", "desc": "d"})

        assert isinstance(error, BadRequestError)
        assert error.status_code == 400

    def test_from_response_returns_unauthorized_error_for_401(self):
        """Test that from_response returns UnauthorizedError for 401 status."""
        response = httpx.Response(
            401,
            json={"code": "c", "desc": "d"},
            request=httpx.Request("GET", "http://test"),
        )
        error = APIError.from_response(response, error_data={"code": "c", "desc": "d"})

        assert isinstance(error, UnauthorizedError)
        assert error.status_code == 401

    def test_from_response_returns_forbidden_error_for_403(self):
        """Test that from_response returns ForbiddenError for 403 status."""
        response = httpx.Response(
            403,
            json={"code": "c", "desc": "d"},
            request=httpx.Request("GET", "http://test"),
        )
        error = APIError.from_response(response, error_data={"code": "c", "desc": "d"})

        assert isinstance(error, ForbiddenError)
        assert error.status_code == 403

    def test_from_response_returns_not_found_error_for_404(self):
        """Test that from_response returns NotFoundError for 404 status."""
        response = httpx.Response(
            404,
            json={"code": "c", "desc": "d"},
            request=httpx.Request("GET", "http://test"),
        )
        error = APIError.from_response(response, error_data={"code": "c", "desc": "d"})

        assert isinstance(error, NotFoundError)
        assert error.status_code == 404

    def test_from_response_returns_too_many_requests_error_for_429(self):
        """Test that from_response returns TooManyRequestsError for 429 status."""
        response = httpx.Response(
            429,
            json={"code": "c", "desc": "d"},
            request=httpx.Request("GET", "http://test"),
        )
        error = APIError.from_response(response, error_data={"code": "c", "desc": "d"})

        assert isinstance(error, TooManyRequestsError)
        assert error.status_code == 429

    def test_from_response_returns_internal_server_error_for_500(self):
        """Test that from_response returns InternalServerError for 500 status."""
        response = httpx.Response(
            500,
            json={"code": "c", "desc": "d"},
            request=httpx.Request("GET", "http://test"),
        )
        error = APIError.from_response(response, error_data={"code": "c", "desc": "d"})

        assert isinstance(error, InternalServerError)
        assert error.status_code == 500

    def test_from_response_returns_internal_server_error_for_503(self):
        """Test that from_response returns InternalServerError for 5xx status."""
        response = httpx.Response(
            503,
            json={"code": "c", "desc": "d"},
            request=httpx.Request("GET", "http://test"),
        )
        error = APIError.from_response(response, error_data={"code": "c", "desc": "d"})

        assert isinstance(error, InternalServerError)
        assert error.status_code == 503

    def test_from_response_uses_error_desc_as_default_message(self):
        """Test that from_response uses error_desc as default message when message not provided."""
        response = httpx.Response(
            400,
            json={"code": "ERR", "desc": "Description from API"},
            request=httpx.Request("GET", "http://test"),
        )
        error = APIError.from_response(
            response, error_data={"code": "ERR", "desc": "Description from API"}
        )

        assert str(error) == "Description from API"

    def test_from_response_uses_http_status_fallback_message(self):
        """Test that from_response uses HTTP status as fallback message."""
        response = httpx.Response(400, request=httpx.Request("GET", "http://test"))
        error = APIError.from_response(response)

        assert str(error) == "HTTP 400 error"

    def test_from_response_returns_generic_api_error_for_other_status(self):
        """Test that from_response returns generic APIError for unhandled status codes."""
        response = httpx.Response(
            418,  # I'm a teapot
            json={"code": "c", "desc": "d"},
            request=httpx.Request("GET", "http://test"),
        )
        error = APIError.from_response(response, error_data={"code": "c", "desc": "d"})

        assert isinstance(error, APIError)
        assert not isinstance(error, BadRequestError)
        assert not isinstance(error, UnauthorizedError)
        assert error.status_code == 418


class TestSpecificErrors:
    """Test specific error subclasses."""

    def test_bad_request_error(self):
        """Test BadRequestError."""
        error = BadRequestError("Bad request", status_code=400)
        assert isinstance(error, APIError)
        assert error.status_code == 400

    def test_unauthorized_error(self):
        """Test UnauthorizedError."""
        error = UnauthorizedError("Unauthorized", status_code=401)
        assert isinstance(error, APIError)
        assert error.status_code == 401

    def test_forbidden_error(self):
        """Test ForbiddenError."""
        error = ForbiddenError("Forbidden", status_code=403)
        assert isinstance(error, APIError)
        assert error.status_code == 403

    def test_not_found_error(self):
        """Test NotFoundError."""
        error = NotFoundError("Not found", status_code=404)
        assert isinstance(error, APIError)
        assert error.status_code == 404

    def test_too_many_requests_error(self):
        """Test TooManyRequestsError."""
        error = TooManyRequestsError("Too many requests", status_code=429)
        assert isinstance(error, APIError)
        assert error.status_code == 429

    def test_internal_server_error(self):
        """Test InternalServerError."""
        error = InternalServerError("Server error", status_code=500)
        assert isinstance(error, APIError)
        assert error.status_code == 500

    def test_connection_error(self):
        """Test ConnectionError."""
        error = ConnectionError("Connection failed")
        assert isinstance(error, PayOSError)
        assert not isinstance(error, APIError)

    def test_webhook_error(self):
        """Test WebhookError."""
        error = WebhookError("Webhook verification failed")
        assert isinstance(error, PayOSError)
        assert not isinstance(error, APIError)
