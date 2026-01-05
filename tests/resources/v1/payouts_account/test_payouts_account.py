"""Tests for payouts account resource."""

import pytest
from pytest_httpx import HTTPXMock

from payos import AsyncPayOS, PayOS
from payos.types.v1 import PayoutAccountInfo

# Constants
CLIENT_ID = "test-client-id"
API_KEY = "test-api-key"
CHECKSUM_KEY = "test-checksum-key"
BASE_URL = "https://api-test.payos.vn"


class TestPayoutsAccount:
    """Synchronous tests for PayoutsAccount."""

    def test_get_balance(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test getting payout account balance successfully."""
        mock_balance = PayoutAccountInfo(
            account_number="0123456789",
            account_name="NGUYEN VAN A",
            balance="5000000",
            currency="VND",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v1/payouts-account/balance",
            method="GET",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_balance.model_dump(by_alias=True),
            },
            status_code=200,
            headers={"x-signature": "mock-signature"},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_sync)

        result = client.payouts_account.balance()

        assert result.account_number == "0123456789"
        assert result.account_name == "NGUYEN VAN A"
        assert result.balance == "5000000"
        assert result.currency == "VND"

    def test_get_balance_different_account(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test getting balance with different account data."""
        mock_balance = PayoutAccountInfo(
            account_number="9876543210",
            account_name="COMPANY ABC",
            balance="10000000",
            currency="VND",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v1/payouts-account/balance",
            method="GET",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_balance.model_dump(by_alias=True),
            },
            status_code=200,
            headers={"x-signature": "mock-signature"},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_sync)

        result = client.payouts_account.balance()

        assert result.account_number == "9876543210"
        assert result.account_name == "COMPANY ABC"
        assert result.balance == "10000000"

    def test_get_balance_zero_balance(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test getting balance with zero balance."""
        mock_balance = PayoutAccountInfo(
            account_number="0123456789",
            account_name="NGUYEN VAN A",
            balance="0",
            currency="VND",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v1/payouts-account/balance",
            method="GET",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_balance.model_dump(by_alias=True),
            },
            status_code=200,
            headers={"x-signature": "mock-signature"},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_sync)

        result = client.payouts_account.balance()

        assert result.account_number == "0123456789"
        assert result.account_name == "NGUYEN VAN A"
        assert result.balance == "0"


class TestAsyncPayoutsAccount:
    """Asynchronous tests for AsyncPayoutsAccount."""

    @pytest.mark.asyncio
    async def test_get_balance(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test getting payout account balance successfully."""
        mock_balance = PayoutAccountInfo(
            account_number="0123456789",
            account_name="NGUYEN VAN A",
            balance="5000000",
            currency="VND",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v1/payouts-account/balance",
            method="GET",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_balance.model_dump(by_alias=True),
            },
            status_code=200,
            headers={"x-signature": "mock-signature"},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_async)

        result = await client.payouts_account.balance()

        assert result.account_number == "0123456789"
        assert result.account_name == "NGUYEN VAN A"
        assert result.balance == "5000000"
        assert result.currency == "VND"

    @pytest.mark.asyncio
    async def test_get_balance_different_account(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test getting balance with different account data."""
        mock_balance = PayoutAccountInfo(
            account_number="9876543210",
            account_name="COMPANY ABC",
            balance="10000000",
            currency="VND",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v1/payouts-account/balance",
            method="GET",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_balance.model_dump(by_alias=True),
            },
            status_code=200,
            headers={"x-signature": "mock-signature"},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_async)

        result = await client.payouts_account.balance()

        assert result.account_number == "9876543210"
        assert result.account_name == "COMPANY ABC"
        assert result.balance == "10000000"

    @pytest.mark.asyncio
    async def test_get_balance_zero_balance(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test getting balance with zero balance."""
        mock_balance = PayoutAccountInfo(
            account_number="0123456789",
            account_name="NGUYEN VAN A",
            balance="0",
            currency="VND",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v1/payouts-account/balance",
            method="GET",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_balance.model_dump(by_alias=True),
            },
            status_code=200,
            headers={"x-signature": "mock-signature"},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_async)

        result = await client.payouts_account.balance()

        assert result.account_number == "0123456789"
        assert result.account_name == "NGUYEN VAN A"
        assert result.balance == "0"
