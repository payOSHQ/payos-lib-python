"""Tests for JSON utilities."""

import json

import httpx
import pytest

from payos.utils.json_utils import (
    build_query_string,
    request_to_dict,
    response_to_dict,
    safe_json_parse,
)


class TestSafeJsonParse:
    """Test safe_json_parse function."""

    def test_parses_valid_json_object(self):
        """Test parsing valid JSON object."""
        result = safe_json_parse('{"a": 1, "b": 2}')
        assert result == {"a": 1, "b": 2}

    def test_parses_valid_json_with_nested_objects(self):
        """Test parsing nested JSON."""
        result = safe_json_parse('{"user": {"name": "John", "age": 30}}')
        assert result == {"user": {"name": "John", "age": 30}}

    def test_parses_empty_object(self):
        """Test parsing empty JSON object."""
        result = safe_json_parse("{}")
        assert result == {}

    def test_returns_none_for_invalid_json(self):
        """Test that invalid JSON returns None."""
        result = safe_json_parse("not-json")
        assert result is None

    def test_returns_none_for_malformed_json(self):
        """Test that malformed JSON returns None."""
        result = safe_json_parse('{"a": 1,}')
        assert result is None

    def test_returns_none_for_empty_string(self):
        """Test that empty string returns None."""
        result = safe_json_parse("")
        assert result is None

    def test_parses_json_with_special_characters(self):
        """Test parsing JSON with special characters."""
        result = safe_json_parse('{"message": "Hello\\nWorld"}')
        assert result == {"message": "Hello\nWorld"}


class TestBuildQueryString:
    """Test build_query_string function."""

    def test_builds_query_string_from_dict(self):
        """Test building query string from simple dict."""
        result = build_query_string({"page": 1, "limit": 10})
        # Note: urlencode may return in any order
        assert "page=1" in result
        assert "limit=10" in result

    def test_filters_out_none_values(self):
        """Test that None values are filtered out."""
        result = build_query_string({"page": 1, "filter": None, "limit": 10})
        assert "page=1" in result
        assert "limit=10" in result
        assert "filter" not in result

    def test_converts_numbers_to_strings(self):
        """Test that numbers are converted to strings."""
        result = build_query_string({"offset": 0, "total": 100})
        assert "offset=0" in result
        assert "total=100" in result

    def test_serializes_dict_values_as_json(self):
        """Test that dict values are JSON serialized."""
        result = build_query_string({"filter": {"status": "active"}})
        assert "filter=" in result
        # The dict should be JSON encoded
        assert "%22status%22" in result or "status" in result

    def test_serializes_list_values_as_json(self):
        """Test that list values are JSON serialized."""
        result = build_query_string({"ids": [1, 2, 3]})
        assert "ids=" in result

    def test_handles_empty_dict(self):
        """Test that empty dict returns empty string."""
        result = build_query_string({})
        assert result == ""

    def test_handles_boolean_values(self):
        """Test that boolean values are converted to strings."""
        result = build_query_string({"active": True, "deleted": False})
        assert "active=True" in result
        assert "deleted=False" in result


class TestRequestToDict:
    """Test request_to_dict function."""

    def test_converts_simple_request(self):
        """Test converting simple GET request."""
        request = httpx.Request("GET", "https://api.example.com/test")
        result = request_to_dict(request)

        assert result["method"] == "GET"
        assert result["url"] == "https://api.example.com/test"
        assert "headers" in result
        assert result["json"] is None

    def test_converts_request_with_json_body(self):
        """Test converting request with JSON body."""
        request = httpx.Request(
            "POST",
            "https://api.example.com/test",
            json={"key": "value"},
        )
        result = request_to_dict(request)

        assert result["method"] == "POST"
        assert result["json"] == {"key": "value"}

    def test_converts_request_with_headers(self):
        """Test converting request with custom headers."""
        request = httpx.Request(
            "GET",
            "https://api.example.com/test",
            headers={"X-Custom": "header-value"},
        )
        result = request_to_dict(request)

        assert "headers" in result
        assert "x-custom" in result["headers"]

    def test_handles_request_with_non_json_body(self):
        """Test converting request with non-JSON body."""
        request = httpx.Request(
            "POST",
            "https://api.example.com/test",
            content=b"plain text body",
        )
        result = request_to_dict(request)

        assert "body" in result
        assert result["body"] == "plain text body"

    def test_handles_request_with_no_content(self):
        """Test converting request with no content."""
        request = httpx.Request("DELETE", "https://api.example.com/test")
        result = request_to_dict(request)

        assert result["json"] is None


class TestResponseToDict:
    """Test response_to_dict function."""

    def test_converts_simple_response(self):
        """Test converting simple response."""
        response = httpx.Response(
            200,
            request=httpx.Request("GET", "https://api.example.com/test"),
        )
        result = response_to_dict(response)

        assert result["status_code"] == 200
        assert result["url"] == "https://api.example.com/test"
        assert "headers" in result

    def test_converts_response_with_json_body(self):
        """Test converting response with JSON body."""
        response = httpx.Response(
            200,
            json={"message": "success"},
            request=httpx.Request("GET", "https://api.example.com/test"),
        )
        result = response_to_dict(response)

        assert result["status_code"] == 200
        assert result["body"] == {"message": "success"}

    def test_converts_response_with_text_body(self):
        """Test converting response with plain text body."""
        response = httpx.Response(
            200,
            content=b"plain text",
            request=httpx.Request("GET", "https://api.example.com/test"),
        )
        result = response_to_dict(response)

        assert result["body"] == "plain text"

    def test_includes_http_version(self):
        """Test that HTTP version is included."""
        response = httpx.Response(
            200,
            request=httpx.Request("GET", "https://api.example.com/test"),
        )
        result = response_to_dict(response)

        assert "http_version" in result

    def test_includes_reason_phrase(self):
        """Test that reason phrase is included."""
        response = httpx.Response(
            404,
            request=httpx.Request("GET", "https://api.example.com/test"),
        )
        result = response_to_dict(response)

        assert "reason_phrase" in result

    def test_converts_response_with_headers(self):
        """Test converting response with headers."""
        response = httpx.Response(
            200,
            headers={"X-Custom": "value"},
            request=httpx.Request("GET", "https://api.example.com/test"),
        )
        result = response_to_dict(response)

        assert "headers" in result
        assert result["headers"]["x-custom"] == "value"
