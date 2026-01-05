"""Tests for payouts resource."""

import pytest
from pytest_httpx import HTTPXMock

from payos import AsyncPayOS, PayOS
from payos.types.v1 import (
    EstimateCredit,
    Payout,
    PayoutRequest,
    PayoutTransaction,
)

# Constants
CLIENT_ID = "test-client-id"
API_KEY = "test-api-key"
CHECKSUM_KEY = "test-checksum-key"
BASE_URL = "https://api-test.payos.vn"


class TestPayouts:
    """Synchronous tests for Payouts."""

    def test_create_with_generated_idempotency_key(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test creating payout with auto-generated idempotency key."""
        payout_request = PayoutRequest(
            reference_id="referenceId",
            amount=2000,
            description="payout",
            to_bin="970422",
            to_account_number="0123456789",
            category=["salary"],
        )

        mock_payout_response = Payout(
            id="payout-id",
            reference_id="referenceId",
            transactions=[
                PayoutTransaction(
                    id="txn-id",
                    reference_id="referenceId",
                    amount=2000,
                    description="payout",
                    to_bin="970422",
                    to_account_number="0123456789",
                    to_account_name="NGUYEN VAN A",
                    reference="FT-REFERENCE",
                    transaction_datetime="2025-12-12T09:00:00+07:00",
                    error_message=None,
                    error_code=None,
                    state="SUCCEEDED",
                ),
            ],
            category=["salary"],
            approval_state="COMPLETED",
            created_at="2025-12-12T09:00:00+07:00",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v1/payouts",
            method="POST",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_payout_response.model_dump(by_alias=True),
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
        mock_crypto_sync.create_uuid4.return_value = "generated-uuid"

        result = client.payouts.create(payout_request)

        assert result.id == "payout-id"
        assert result.approval_state == "COMPLETED"

    def test_create_with_custom_idempotency_key(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test creating payout with custom idempotency key."""
        payout_request = PayoutRequest(
            reference_id="referenceId",
            amount=2000,
            description="payout",
            to_bin="970422",
            to_account_number="0123456789",
            category=["salary"],
        )

        custom_idempotency_key = "custom-uuid-12345"

        mock_payout_response = Payout(
            id="payout-id",
            reference_id="referenceId",
            transactions=[],
            category=["salary"],
            approval_state="COMPLETED",
            created_at="2025-12-12T09:00:00+07:00",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v1/payouts",
            method="POST",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_payout_response.model_dump(by_alias=True),
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

        result = client.payouts.create(payout_request, idempotency_key=custom_idempotency_key)

        assert result.id == "payout-id"

    def test_create_without_category(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test creating payout without category."""
        payout_request = PayoutRequest(
            reference_id="referenceId",
            amount=2000,
            description="payout",
            to_bin="970422",
            to_account_number="0123456789",
        )

        mock_payout_response = Payout(
            id="payout-id",
            reference_id="referenceId",
            transactions=[],
            category=None,
            approval_state="COMPLETED",
            created_at="2025-12-12T09:00:00+07:00",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v1/payouts",
            method="POST",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_payout_response.model_dump(by_alias=True),
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

        result = client.payouts.create(payout_request)

        assert result.category is None

    def test_get_completed_state(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test getting payout with COMPLETED state."""
        payout_id = "payout-123"
        mock_payout = Payout(
            id=payout_id,
            reference_id="referenceId",
            transactions=[
                PayoutTransaction(
                    id="txn-id",
                    reference_id="referenceId",
                    amount=2000,
                    description="batch payout",
                    to_bin="970422",
                    to_account_number="0123456789",
                    to_account_name="NGUYEN VAN A",
                    reference="FT-REFERENCE",
                    transaction_datetime="2025-12-12T09:00:00+07:00",
                    error_message=None,
                    error_code=None,
                    state="SUCCEEDED",
                )
            ],
            category=["salary"],
            approval_state="COMPLETED",
            created_at="2025-12-12T09:00:00+07:00",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v1/payouts/{payout_id}",
            method="GET",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_payout.model_dump(by_alias=True),
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

        result = client.payouts.get(payout_id)

        assert result.approval_state == "COMPLETED"

    def test_get_failed_state(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test getting payout with FAILED state."""
        payout_id = "payout-failed"
        mock_failed_payout = Payout(
            id=payout_id,
            reference_id="referenceId",
            transactions=[
                PayoutTransaction(
                    id="txn-id",
                    reference_id="referenceId",
                    amount=2000,
                    description="batch payout",
                    to_bin="970422",
                    to_account_number="0123456789",
                    to_account_name="NGUYEN VAN A",
                    reference=None,
                    transaction_datetime=None,
                    error_message="error message",
                    error_code="error code",
                    state="FAILED",
                )
            ],
            category=None,
            approval_state="FAILED",
            created_at="2025-12-12T09:00:00+07:00",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v1/payouts/{payout_id}",
            method="GET",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_failed_payout.model_dump(by_alias=True),
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

        result = client.payouts.get(payout_id)

        assert result.approval_state == "FAILED"
        assert result.transactions[0].state == "FAILED"

    def test_estimate_credit_single(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test estimating credit for single payout."""
        payout_request = PayoutRequest(
            reference_id="ref-123",
            amount=5000,
            description="salary",
            to_bin="970422",
            to_account_number="0123456789",
            category=["salary"],
        )

        mock_estimate = EstimateCredit(estimate_credit=5100)

        httpx_mock.add_response(
            url=f"{BASE_URL}/v1/payouts/estimate-credit",
            method="POST",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_estimate.model_dump(by_alias=True),
            },
            status_code=200,
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_sync)

        result = client.payouts.estimate_credit(payout_request)

        assert result.estimate_credit == 5100

    def test_list_default_pagination(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test listing payouts with default pagination."""
        mock_payout = {
            "id": "payout-1",
            "referenceId": "ref-1",
            "transactions": [],
            "category": ["salary"],
            "approvalState": "COMPLETED",
            "createdAt": "2025-12-12T09:00:00+07:00",
        }

        httpx_mock.add_response(
            url=f"{BASE_URL}/v1/payouts",
            method="GET",
            json={
                "code": "00",
                "desc": "success",
                "data": {
                    "payouts": [mock_payout],
                    "pagination": {
                        "limit": 10,
                        "offset": 0,
                        "total": 1,
                        "count": 1,
                        "hasMore": False,
                    },
                },
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

        result = client.payouts.list()

        assert len(result.data) == 1
        assert result.data[0].id == "payout-1"


class TestAsyncPayouts:
    """Asynchronous tests for AsyncPayouts."""

    @pytest.mark.asyncio
    async def test_create_with_generated_idempotency_key(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test creating payout with auto-generated idempotency key."""
        payout_request = PayoutRequest(
            reference_id="referenceId",
            amount=2000,
            description="payout",
            to_bin="970422",
            to_account_number="0123456789",
            category=["salary"],
        )

        mock_payout_response = Payout(
            id="payout-id",
            reference_id="referenceId",
            transactions=[
                PayoutTransaction(
                    id="txn-id",
                    reference_id="referenceId",
                    amount=2000,
                    description="payout",
                    to_bin="970422",
                    to_account_number="0123456789",
                    to_account_name="NGUYEN VAN A",
                    reference="FT-REFERENCE",
                    transaction_datetime="2025-12-12T09:00:00+07:00",
                    error_message=None,
                    error_code=None,
                    state="SUCCEEDED",
                )
            ],
            category=["salary"],
            approval_state="COMPLETED",
            created_at="2025-12-12T09:00:00+07:00",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v1/payouts",
            method="POST",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_payout_response.model_dump(by_alias=True),
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
        mock_crypto_async.create_uuid4.return_value = "generated-uuid"

        result = await client.payouts.create(payout_request)

        assert result.id == "payout-id"
        assert result.approval_state == "COMPLETED"

    @pytest.mark.asyncio
    async def test_create_with_custom_idempotency_key(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test creating payout with custom idempotency key."""
        payout_request = PayoutRequest(
            reference_id="referenceId",
            amount=2000,
            description="payout",
            to_bin="970422",
            to_account_number="0123456789",
            category=["salary"],
        )

        custom_idempotency_key = "custom-uuid-12345"

        mock_payout_response = Payout(
            id="payout-id",
            reference_id="referenceId",
            transactions=[],
            category=["salary"],
            approval_state="COMPLETED",
            created_at="2025-12-12T09:00:00+07:00",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v1/payouts",
            method="POST",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_payout_response.model_dump(by_alias=True),
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

        result = await client.payouts.create(payout_request, idempotency_key=custom_idempotency_key)

        assert result.id == "payout-id"

    @pytest.mark.asyncio
    async def test_get_completed_state(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test getting payout with COMPLETED state."""
        payout_id = "payout-123"
        mock_payout = Payout(
            id=payout_id,
            reference_id="referenceId",
            transactions=[
                PayoutTransaction(
                    id="txn-id",
                    reference_id="referenceId",
                    amount=2000,
                    description="batch payout",
                    to_bin="970422",
                    to_account_number="0123456789",
                    to_account_name="NGUYEN VAN A",
                    reference="FT-REFERENCE",
                    transaction_datetime="2025-12-12T09:00:00+07:00",
                    error_message=None,
                    error_code=None,
                    state="SUCCEEDED",
                )
            ],
            category=["salary"],
            approval_state="COMPLETED",
            created_at="2025-12-12T09:00:00+07:00",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v1/payouts/{payout_id}",
            method="GET",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_payout.model_dump(by_alias=True),
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

        result = await client.payouts.get(payout_id)

        assert result.approval_state == "COMPLETED"

    @pytest.mark.asyncio
    async def test_estimate_credit_single(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test estimating credit for single payout."""
        payout_request = PayoutRequest(
            reference_id="ref-123",
            amount=5000,
            description="salary",
            to_bin="970422",
            to_account_number="0123456789",
            category=["salary"],
        )

        mock_estimate = EstimateCredit(estimate_credit=5100)

        httpx_mock.add_response(
            url=f"{BASE_URL}/v1/payouts/estimate-credit",
            method="POST",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_estimate.model_dump(by_alias=True),
            },
            status_code=200,
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_async)

        result = await client.payouts.estimate_credit(payout_request)

        assert result.estimate_credit == 5100

    @pytest.mark.asyncio
    async def test_list_default_pagination(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test listing payouts with default pagination."""
        mock_payout = {
            "id": "payout-1",
            "referenceId": "ref-1",
            "transactions": [],
            "category": ["salary"],
            "approvalState": "COMPLETED",
            "createdAt": "2025-12-12T09:00:00+07:00",
        }

        httpx_mock.add_response(
            url=f"{BASE_URL}/v1/payouts",
            method="GET",
            json={
                "code": "00",
                "desc": "success",
                "data": {
                    "payouts": [mock_payout],
                    "pagination": {
                        "limit": 10,
                        "offset": 0,
                        "total": 1,
                        "count": 1,
                        "hasMore": False,
                    },
                },
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

        result = await client.payouts.list()

        assert len(result.data) == 1
        assert result.data[0].id == "payout-1"
