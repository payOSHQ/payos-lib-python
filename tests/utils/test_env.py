"""Tests for environment utilities."""

import os

import pytest

from payos.utils.env import get_env_var


class TestGetEnvVar:
    """Test get_env_var function."""

    def test_reads_from_os_environ_when_present(self, monkeypatch: pytest.MonkeyPatch):
        """Test reading from os.environ when variable exists."""
        monkeypatch.setenv("FOO", "bar")
        result = get_env_var("FOO")
        assert result == "bar"

    def test_reads_from_os_environ_with_whitespace(self, monkeypatch: pytest.MonkeyPatch):
        """Test reading from os.environ with whitespace (not trimmed in Python)."""
        monkeypatch.setenv("FOO", "  bar  ")
        result = get_env_var("FOO")
        # Python os.environ doesn't auto-trim, value is returned as-is
        assert result == "  bar  "

    def test_returns_none_when_not_present(self, monkeypatch: pytest.MonkeyPatch):
        """Test returns None when variable doesn't exist."""
        monkeypatch.delenv("NOPE", raising=False)
        result = get_env_var("NOPE")
        assert result is None

    def test_returns_default_when_not_present(self, monkeypatch: pytest.MonkeyPatch):
        """Test returns default value when variable doesn't exist."""
        monkeypatch.delenv("NOPE", raising=False)
        result = get_env_var("NOPE", default="fallback")
        assert result == "fallback"

    def test_ignores_default_when_variable_present(self, monkeypatch: pytest.MonkeyPatch):
        """Test ignores default when variable exists."""
        monkeypatch.setenv("EXISTS", "value")
        result = get_env_var("EXISTS", default="fallback")
        assert result == "value"

    def test_empty_string_is_considered_present(self, monkeypatch: pytest.MonkeyPatch):
        """Test that empty string is treated as present (not None)."""
        monkeypatch.setenv("EMPTY", "")
        result = get_env_var("EMPTY")
        assert result == ""
        assert result is not None
