"""Tests for body-signed response data validation."""

import pytest

from payos import InvalidSignatureError
from payos.utils.response_validation import validate_response_data


class TestValidateResponseData:
    """Test validate_response_data function."""

    def test_accepts_payment_link(self):
        """Test that a realistic payment link with transactions is accepted."""
        validate_response_data(
            {
                "id": "abc",
                "orderCode": 123,
                "amount": 2000,
                "status": "PAID",
                "canceledAt": None,
                "transactions": [
                    {"reference": "FT1", "amount": 2000, "description": "x y", "bankId": None}
                ],
                "flag": True,
                "rate": 1.5,
            }
        )

    @pytest.mark.parametrize(
        "data",
        [
            [1],
            None,
            {"a": "x&b=1"},
            {"a": {"b": 1}},
            {"a-b": 1},
            {"a\n": 1},
            {"a": [{"b\n": 1}]},
            {"__proto__": 1},
            {"a": [{"b": {"c": 1}}]},
            {"a": [[1]]},
            {"a": float("inf")},
            {"a": float("nan")},
            {"a": 2**53},
            {"a": 1e300},
        ],
    )
    def test_rejects_unsafe_data(self, data):
        """Test that data able to alter the signed string is rejected."""
        with pytest.raises(InvalidSignatureError):
            validate_response_data(data)
