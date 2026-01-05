"""Tests for crypto provider."""

import json
import os
import re
from pathlib import Path

import pytest

from payos._crypto.provider import CryptoProvider

# Test constants
CHECKSUM_KEY = "test_checksum_key"

# Load test cases from JSON file
TEST_CASES_PATH = Path(__file__).parent / "testCases.json"
with open(TEST_CASES_PATH, "r", encoding="utf-8") as f:
    ALL_TEST_CASES = json.load(f)

# Filter test cases by type
BODY_TEST_CASES = [tc for tc in ALL_TEST_CASES if tc["type"] == "body"]
CREATE_PAYMENT_LINK_TEST_CASES = [tc for tc in ALL_TEST_CASES if tc["type"] == "create-payment-link"]
HEADER_TEST_CASES = [tc for tc in ALL_TEST_CASES if tc["type"] == "header"]


class TestCreateSignatureFromObject:
    """Test create_signature_from_object method with 'body' type test cases."""

    @pytest.mark.parametrize(
        "test_case",
        BODY_TEST_CASES,
        ids=lambda tc: tc["caseName"],
    )
    def test_body_signature(self, test_case):
        """Test signature generation from object data."""
        crypto = CryptoProvider()
        result = crypto.create_signature_from_object(test_case["payload"], CHECKSUM_KEY)
        assert result == test_case["expect"]


class TestCreateSignatureOfPaymentRequest:
    """Test create_signature_of_payment_request method with 'create-payment-link' type test cases."""

    @pytest.mark.parametrize(
        "test_case",
        CREATE_PAYMENT_LINK_TEST_CASES,
        ids=lambda tc: tc["caseName"],
    )
    def test_payment_request_signature(self, test_case):
        """Test signature generation for payment requests."""
        crypto = CryptoProvider()
        result = crypto.create_signature_of_payment_request(test_case["payload"], CHECKSUM_KEY)
        assert result == test_case["expect"]


class TestCreateSignature:
    """Test create_signature method with 'header' type test cases."""

    @pytest.mark.parametrize(
        "test_case",
        HEADER_TEST_CASES,
        ids=lambda tc: tc["caseName"],
    )
    def test_header_signature(self, test_case):
        """Test signature generation with default options."""
        crypto = CryptoProvider()
        result = crypto.create_signature(CHECKSUM_KEY, test_case["payload"])
        assert result == test_case["expect"]


class TestEdgeCases:
    """Test edge cases and utility methods."""

    def test_create_signature_from_object_returns_none_with_empty_key(self):
        """Test that create_signature_from_object returns None when key is empty."""
        crypto = CryptoProvider()
        result = crypto.create_signature_from_object({"field": "value"}, "")
        assert result is None

    def test_create_signature_from_object_returns_none_with_empty_data(self):
        """Test that create_signature_from_object handles empty dict (generates signature for empty query string)."""
        crypto = CryptoProvider()
        result = crypto.create_signature_from_object({}, CHECKSUM_KEY)
        # Empty dict should produce a signature, not None
        assert result is not None
        assert isinstance(result, str)

    def test_create_signature_from_object_returns_none_with_none_data(self):
        """Test that create_signature_from_object returns None when data is None."""
        crypto = CryptoProvider()
        result = crypto.create_signature_from_object(None, CHECKSUM_KEY)
        assert result is None

    def test_create_signature_of_payment_request_returns_none_with_empty_key(self):
        """Test that create_signature_of_payment_request returns None when key is empty."""
        crypto = CryptoProvider()
        payment_data = {
            "amount": 2000,
            "description": "test",
            "orderCode": 123,
            "cancelUrl": "http://localhost",
            "returnUrl": "http://localhost",
        }
        result = crypto.create_signature_of_payment_request(payment_data, "")
        assert result is None

    def test_create_signature_of_payment_request_returns_none_with_empty_data(self):
        """Test that create_signature_of_payment_request returns None when required fields are missing."""
        crypto = CryptoProvider()
        # Empty dict lacks required fields, should return None
        result = crypto.create_signature_of_payment_request({}, CHECKSUM_KEY)
        assert result is None

    def test_create_signature_of_payment_request_returns_none_with_none_data(self):
        """Test that create_signature_of_payment_request returns None when data is None."""
        crypto = CryptoProvider()
        result = crypto.create_signature_of_payment_request(None, CHECKSUM_KEY)
        assert result is None

    def test_create_signature_of_payment_request_returns_none_with_missing_required_field(self):
        """Test that create_signature_of_payment_request returns None when required field is missing."""
        crypto = CryptoProvider()
        # Missing 'amount' field
        incomplete_data = {
            "description": "test",
            "orderCode": 123,
            "cancelUrl": "http://localhost",
            "returnUrl": "http://localhost",
        }
        result = crypto.create_signature_of_payment_request(incomplete_data, CHECKSUM_KEY)
        assert result is None

    def test_create_uuid4_returns_valid_uuid(self):
        """Test that create_uuid4 returns a valid UUID v4."""
        crypto = CryptoProvider()
        uuid = crypto.create_uuid4()

        # UUID v4 format: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
        # where y is 8, 9, a, or b
        uuid_v4_regex = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", re.IGNORECASE
        )
        assert uuid_v4_regex.match(uuid), f"Generated UUID '{uuid}' does not match UUID v4 format"

    def test_create_uuid4_produces_unique_values(self):
        """Test that create_uuid4 produces unique values."""
        crypto = CryptoProvider()
        uuid1 = crypto.create_uuid4()
        uuid2 = crypto.create_uuid4()

        assert uuid1 != uuid2, "Two consecutive UUID generations should produce different values"

    def test_create_signature_with_different_algorithms(self):
        """Test create_signature supports different hash algorithms."""
        crypto = CryptoProvider()
        data = {"field": "value"}

        # Test SHA256 (default)
        sha256_sig = crypto.create_signature(CHECKSUM_KEY, data, algorithm="sha256")
        assert sha256_sig is not None
        assert len(sha256_sig) == 64  # SHA256 produces 64 hex characters

        # Test SHA512
        sha512_sig = crypto.create_signature(CHECKSUM_KEY, data, algorithm="sha512")
        assert sha512_sig is not None
        assert len(sha512_sig) == 128  # SHA512 produces 128 hex characters

        # Test SHA1
        sha1_sig = crypto.create_signature(CHECKSUM_KEY, data, algorithm="sha1")
        assert sha1_sig is not None
        assert len(sha1_sig) == 40  # SHA1 produces 40 hex characters

        # Test MD5
        md5_sig = crypto.create_signature(CHECKSUM_KEY, data, algorithm="md5")
        assert md5_sig is not None
        assert len(md5_sig) == 32  # MD5 produces 32 hex characters

    def test_create_signature_with_unsupported_algorithm_raises_error(self):
        """Test that create_signature raises ValueError for unsupported algorithms."""
        crypto = CryptoProvider()
        data = {"field": "value"}

        with pytest.raises(ValueError, match="Unsupported algorithm"):
            crypto.create_signature(CHECKSUM_KEY, data, algorithm="unsupported")

    def test_create_signature_with_encode_uri_false(self):
        """Test create_signature with encode_uri=False option."""
        crypto = CryptoProvider()
        data = {"field": "value with spaces"}

        # With encoding (default)
        encoded_sig = crypto.create_signature(CHECKSUM_KEY, data, encode_uri=True)

        # Without encoding
        unencoded_sig = crypto.create_signature(CHECKSUM_KEY, data, encode_uri=False)

        # Signatures should be different when encoding is toggled
        assert encoded_sig != unencoded_sig

    def test_create_signature_with_sort_arrays_true(self):
        """Test create_signature with sort_arrays=True option."""
        crypto = CryptoProvider()
        data = {"items": [{"name": "b"}, {"name": "a"}]}

        # Without array sorting (default)
        unsorted_sig = crypto.create_signature(CHECKSUM_KEY, data, sort_arrays=False)

        # With array sorting
        sorted_sig = crypto.create_signature(CHECKSUM_KEY, data, sort_arrays=True)

        # Signatures should be different when sort_arrays is toggled
        assert unsorted_sig != sorted_sig
