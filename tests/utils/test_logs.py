"""Tests for logging utilities."""

import logging

import pytest

from payos.utils.logs import SensitiveHeadersFilter, setup_logging


class TestSetupLogging:
    """Test setup_logging function."""

    def test_sets_log_level_from_string(self, monkeypatch: pytest.MonkeyPatch):
        """Test setting log level from string."""
        # Clear environment variable
        monkeypatch.delenv("PAYOS_LOG", raising=False)

        # Setup with string level
        setup_logging("DEBUG")

        logger = logging.getLogger("payos")
        assert logger.level == logging.DEBUG

    def test_sets_log_level_from_int(self, monkeypatch: pytest.MonkeyPatch):
        """Test setting log level from int."""
        monkeypatch.delenv("PAYOS_LOG", raising=False)

        setup_logging(logging.INFO)

        logger = logging.getLogger("payos")
        assert logger.level == logging.INFO

    def test_sets_log_level_case_insensitive(self, monkeypatch: pytest.MonkeyPatch):
        """Test that string log level is case insensitive."""
        monkeypatch.delenv("PAYOS_LOG", raising=False)

        setup_logging("info")

        logger = logging.getLogger("payos")
        assert logger.level == logging.INFO

    def test_defaults_to_warning_for_invalid_string(self, monkeypatch: pytest.MonkeyPatch):
        """Test that invalid string defaults to WARNING."""
        monkeypatch.delenv("PAYOS_LOG", raising=False)

        setup_logging("invalid")

        logger = logging.getLogger("payos")
        assert logger.level == logging.WARNING

    def test_reads_from_payos_log_env_var_debug(self, monkeypatch: pytest.MonkeyPatch):
        """Test reading DEBUG level from PAYOS_LOG env var."""
        monkeypatch.setenv("PAYOS_LOG", "debug")

        setup_logging()

        logger = logging.getLogger("payos")
        assert logger.level == logging.DEBUG

    def test_reads_from_payos_log_env_var_info(self, monkeypatch: pytest.MonkeyPatch):
        """Test reading INFO level from PAYOS_LOG env var."""
        monkeypatch.setenv("PAYOS_LOG", "info")

        setup_logging()

        logger = logging.getLogger("payos")
        assert logger.level == logging.INFO

    def test_defaults_to_warning_when_no_env_var(self, monkeypatch: pytest.MonkeyPatch):
        """Test defaults to WARNING when no env var set."""
        monkeypatch.delenv("PAYOS_LOG", raising=False)

        setup_logging()

        logger = logging.getLogger("payos")
        assert logger.level == logging.WARNING

    def test_sets_httpx_logger_level(self, monkeypatch: pytest.MonkeyPatch):
        """Test that httpx logger level is also set."""
        monkeypatch.delenv("PAYOS_LOG", raising=False)

        setup_logging(logging.DEBUG)

        httpx_logger = logging.getLogger("httpx")
        assert httpx_logger.level == logging.DEBUG

    def test_explicit_level_overrides_env_var(self, monkeypatch: pytest.MonkeyPatch):
        """Test that explicit level parameter overrides env var."""
        monkeypatch.setenv("PAYOS_LOG", "debug")

        setup_logging("ERROR")

        logger = logging.getLogger("payos")
        assert logger.level == logging.ERROR


class TestSensitiveHeadersFilter:
    """Test SensitiveHeadersFilter."""

    def test_redacts_x_client_id_header(self):
        """Test that x-client-id header is redacted."""
        filter = SensitiveHeadersFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Request",
            args=(),
            exc_info=None,
        )
        # Manually set args as dict (bypassing constructor validation)
        record.args = {"headers": {"x-client-id": "secret123"}}

        result = filter.filter(record)

        assert result is True
        assert record.args["headers"]["x-client-id"] == "<redacted>"

    def test_redacts_x_api_key_header(self):
        """Test that x-api-key header is redacted."""
        filter = SensitiveHeadersFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Request",
            args=(),
            exc_info=None,
        )
        record.args = {"headers": {"x-api-key": "secret-key"}}

        result = filter.filter(record)

        assert result is True
        assert record.args["headers"]["x-api-key"] == "<redacted>"

    def test_redacts_authorization_header(self):
        """Test that authorization header is redacted."""
        filter = SensitiveHeadersFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Request",
            args=(),
            exc_info=None,
        )
        record.args = {"headers": {"Authorization": "Bearer token123"}}

        result = filter.filter(record)

        assert result is True
        assert record.args["headers"]["Authorization"] == "<redacted>"

    def test_redacts_cookie_header(self):
        """Test that cookie header is redacted."""
        filter = SensitiveHeadersFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Request",
            args=(),
            exc_info=None,
        )
        record.args = {"headers": {"Cookie": "session=abc123"}}

        result = filter.filter(record)

        assert result is True
        assert record.args["headers"]["Cookie"] == "<redacted>"

    def test_redacts_set_cookie_header(self):
        """Test that set-cookie header is redacted."""
        filter = SensitiveHeadersFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Response",
            args=(),
            exc_info=None,
        )
        record.args = {"headers": {"Set-Cookie": "session=xyz789"}}

        result = filter.filter(record)

        assert result is True
        assert record.args["headers"]["Set-Cookie"] == "<redacted>"

    def test_case_insensitive_header_matching(self):
        """Test that header matching is case insensitive."""
        filter = SensitiveHeadersFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Request",
            args=(),
            exc_info=None,
        )
        record.args = {"headers": {"X-CLIENT-ID": "secret", "X-Api-Key": "key"}}

        result = filter.filter(record)

        assert result is True
        assert record.args["headers"]["X-CLIENT-ID"] == "<redacted>"
        assert record.args["headers"]["X-Api-Key"] == "<redacted>"

    def test_preserves_non_sensitive_headers(self):
        """Test that non-sensitive headers are preserved."""
        filter = SensitiveHeadersFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Request",
            args=(),
            exc_info=None,
        )
        record.args = {
            "headers": {
                "x-client-id": "secret",
                "content-type": "application/json",
                "user-agent": "payos-python/1.0",
            }
        }

        result = filter.filter(record)

        assert result is True
        assert record.args["headers"]["x-client-id"] == "<redacted>"
        assert record.args["headers"]["content-type"] == "application/json"
        assert record.args["headers"]["user-agent"] == "payos-python/1.0"

    def test_handles_record_without_headers(self):
        """Test that filter handles records without headers."""
        filter = SensitiveHeadersFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Message without headers",
            args=(),
            exc_info=None,
        )
        record.args = {"data": "some data"}

        result = filter.filter(record)

        assert result is True
        assert record.args == {"data": "some data"}

    def test_handles_record_with_non_dict_args(self):
        """Test that filter handles records with non-dict args."""
        filter = SensitiveHeadersFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Simple message %s",
            args=("value",),
            exc_info=None,
        )

        result = filter.filter(record)

        assert result is True
        assert record.args == ("value",)

    def test_creates_copy_of_headers_dict(self):
        """Test that filter creates a copy of headers dict to avoid mutation."""
        filter = SensitiveHeadersFilter()

        original_headers = {"x-client-id": "secret", "content-type": "application/json"}

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Request",
            args=(),
            exc_info=None,
        )
        record.args = {"headers": original_headers}

        filter.filter(record)

        # Original headers should not be mutated
        assert original_headers["x-client-id"] == "secret"
        # Record headers should be redacted
        assert record.args["headers"]["x-client-id"] == "<redacted>"
