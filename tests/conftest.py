"""Shared pytest fixtures for payOS tests."""

import pytest
from unittest.mock import Mock


@pytest.fixture
def test_credentials():
    """Standard test credentials for creating clients."""
    return {
        "client_id": "test-client-id",
        "api_key": "test-api-key",
        "checksum_key": "test-checksum-key",
        "base_url": "https://api-test.payos.vn",
    }


@pytest.fixture
def mock_signature():
    """Standard mock signature value."""
    return "mock-signature"


@pytest.fixture
def mock_crypto_sync(mock_signature):
    """Mock crypto provider for sync client."""
    mock = Mock()
    mock.create_signature_of_payment_request.return_value = mock_signature
    mock.create_signature_from_object.return_value = mock_signature
    mock.create_signature.return_value = mock_signature
    mock.create_uuid4.return_value = "generated-uuid"
    return mock


@pytest.fixture
def mock_crypto_async(mock_signature):
    """Mock crypto provider for async client."""
    mock = Mock()
    mock.create_signature_of_payment_request.return_value = mock_signature
    mock.create_signature_from_object.return_value = mock_signature
    mock.create_signature.return_value = mock_signature
    mock.create_uuid4.return_value = "generated-uuid"
    return mock
