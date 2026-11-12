"""Tests for path segment encoding."""

import pytest

from payos import PayOSError
from payos.utils.path import encode_path_segment


class TestEncodePathSegment:
    """Test encode_path_segment function."""

    def test_percent_encodes_strings(self):
        """Test that path delimiters are encoded so the value stays a single segment."""
        assert (
            encode_path_segment("id", "../../v1/payouts-account/balance")
            == "..%2F..%2Fv1%2Fpayouts-account%2Fbalance"
        )
        assert encode_path_segment("id", "a?b#c%d") == "a%3Fb%23c%25d"

    def test_accepts_safe_integers(self):
        """Test that non-negative safe integers are returned as is."""
        assert encode_path_segment("id", 0) == "0"
        assert encode_path_segment("id", 2**53 - 1) == str(2**53 - 1)

    @pytest.mark.parametrize("value", ["", ".", "..", -1, 2**53, True, 1.0, None])
    def test_rejects_unsafe_values(self, value):
        """Test that empty, dot segment, negative, unsafe and non-integer values are rejected."""
        with pytest.raises(PayOSError):
            encode_path_segment("id", value)
