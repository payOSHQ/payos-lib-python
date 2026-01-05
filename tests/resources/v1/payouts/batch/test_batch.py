"""Tests for batch payout resource."""

import pytest
from pytest_httpx import HTTPXMock

from payos import AsyncPayOS, PayOS
from payos.types.v1 import Payout, PayoutBatchItem, PayoutBatchRequest, PayoutTransaction

# Constants
CLIENT_ID = "test-client-id"
API_KEY = "test-api-key"
CHECKSUM_KEY = "test-checksum-key"
BASE_URL = "https://api-test.payos.vn"


class TestBatch:
    """Synchronous tests for Batch."""

    def test_create_batch_single_item(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test creating batch payout with single item."""
        batch_request = PayoutBatchRequest(
            reference_id="batch-ref-1",
            category=["salary"],
            validate_destination=True,
            payouts=[
                PayoutBatchItem(
                    reference_id="ref-1",
                    amount=2000,
                    description="batch payout",
                    to_bin="970422",
                    to_account_number="0123456789",
                )
            ],
        )

        mock_payout_response = Payout(
            id="batch-id",
            reference_id="batch-ref-1",
            transactions=[
                PayoutTransaction(
                    id="txn-id",
                    reference_id="ref-1",
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
            url=f"{BASE_URL}/v1/payouts/batch",
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

        result = client.payouts.batch.create(batch_request)

        assert result.id == "batch-id"
        assert result.reference_id == "batch-ref-1"
        assert len(result.transactions) == 1
        assert result.transactions[0].state == "SUCCEEDED"
        assert result.approval_state == "COMPLETED"
        assert result.category == ["salary"]

    def test_create_batch_multiple_items(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test creating batch payout with multiple items."""
        batch_request = PayoutBatchRequest(
            reference_id="batch-ref-multi",
            category=["salary", "bonus"],
            validate_destination=True,
            payouts=[
                PayoutBatchItem(
                    reference_id="ref-1",
                    amount=2000,
                    description="batch payout 1",
                    to_bin="970422",
                    to_account_number="0123456789",
                ),
                PayoutBatchItem(
                    reference_id="ref-2",
                    amount=3000,
                    description="batch payout 2",
                    to_bin="970422",
                    to_account_number="9876543210",
                ),
                PayoutBatchItem(
                    reference_id="ref-3",
                    amount=1500,
                    description="batch payout 3",
                    to_bin="970422",
                    to_account_number="1122334455",
                ),
            ],
        )

        mock_payout_response = Payout(
            id="batch-id-multi",
            reference_id="batch-ref-multi",
            transactions=[
                PayoutTransaction(
                    id="txn-1",
                    reference_id="ref-1",
                    amount=2000,
                    description="batch payout 1",
                    to_bin="970422",
                    to_account_number="0123456789",
                    to_account_name="NGUYEN VAN A",
                    reference="FT-REF-1",
                    transaction_datetime="2025-12-12T09:00:00+07:00",
                    error_message=None,
                    error_code=None,
                    state="SUCCEEDED",
                ),
                PayoutTransaction(
                    id="txn-2",
                    reference_id="ref-2",
                    amount=3000,
                    description="batch payout 2",
                    to_bin="970422",
                    to_account_number="9876543210",
                    to_account_name="TRAN THI B",
                    reference="FT-REF-2",
                    transaction_datetime="2025-12-12T09:00:00+07:00",
                    error_message=None,
                    error_code=None,
                    state="SUCCEEDED",
                ),
                PayoutTransaction(
                    id="txn-3",
                    reference_id="ref-3",
                    amount=1500,
                    description="batch payout 3",
                    to_bin="970422",
                    to_account_number="1122334455",
                    to_account_name="LE VAN C",
                    reference="FT-REF-3",
                    transaction_datetime="2025-12-12T09:00:00+07:00",
                    error_message=None,
                    error_code=None,
                    state="SUCCEEDED",
                ),
            ],
            category=["salary", "bonus"],
            approval_state="COMPLETED",
            created_at="2025-12-12T09:00:00+07:00",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v1/payouts/batch",
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

        result = client.payouts.batch.create(batch_request)

        assert result.id == "batch-id-multi"
        assert result.reference_id == "batch-ref-multi"
        assert len(result.transactions) == 3
        assert result.category == ["salary", "bonus"]
        assert result.approval_state == "COMPLETED"

    def test_create_batch_without_category(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test creating batch payout without category."""
        batch_request = PayoutBatchRequest(
            reference_id="batch-ref-no-cat",
            category=None,
            validate_destination=False,
            payouts=[
                PayoutBatchItem(
                    reference_id="ref-1",
                    amount=2000,
                    description="batch payout",
                    to_bin="970422",
                    to_account_number="0123456789",
                )
            ],
        )

        mock_payout_response = Payout(
            id="batch-id",
            reference_id="batch-ref-no-cat",
            transactions=[
                PayoutTransaction(
                    id="txn-id",
                    reference_id="ref-1",
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
            category=None,
            approval_state="COMPLETED",
            created_at="2025-12-12T09:00:00+07:00",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v1/payouts/batch",
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

        result = client.payouts.batch.create(batch_request)

        assert result.id == "batch-id"
        assert result.reference_id == "batch-ref-no-cat"
        assert result.category is None

    def test_create_batch_custom_idempotency_key(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test creating batch payout with custom idempotency key."""
        custom_idempotency_key = "custom-batch-uuid-12345"

        batch_request = PayoutBatchRequest(
            reference_id="batch-ref",
            category=["salary"],
            validate_destination=True,
            payouts=[
                PayoutBatchItem(
                    reference_id="ref-1",
                    amount=2000,
                    description="batch payout",
                    to_bin="970422",
                    to_account_number="0123456789",
                )
            ],
        )

        mock_payout_response = Payout(
            id="batch-id",
            reference_id="batch-ref",
            transactions=[
                PayoutTransaction(
                    id="txn-id",
                    reference_id="ref-1",
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
            url=f"{BASE_URL}/v1/payouts/batch",
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

        result = client.payouts.batch.create(batch_request, idempotency_key=custom_idempotency_key)

        assert result.id == "batch-id"
        assert result.reference_id == "batch-ref"

        request = httpx_mock.get_request()
        assert request is not None
        assert request.headers["x-idempotency-key"] == custom_idempotency_key

    def test_create_batch_partial_completed(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test creating batch payout with PARTIAL_COMPLETED state."""
        batch_request = PayoutBatchRequest(
            reference_id="batch-ref-partial",
            category=["salary"],
            validate_destination=True,
            payouts=[
                PayoutBatchItem(
                    reference_id="ref-1",
                    amount=2000,
                    description="batch payout 1",
                    to_bin="970422",
                    to_account_number="0123456789",
                ),
                PayoutBatchItem(
                    reference_id="ref-2",
                    amount=3000,
                    description="batch payout 2",
                    to_bin="970422",
                    to_account_number="9999999999",
                ),
            ],
        )

        mock_payout_response = Payout(
            id="batch-id-partial",
            reference_id="batch-ref-partial",
            transactions=[
                PayoutTransaction(
                    id="txn-1",
                    reference_id="ref-1",
                    amount=2000,
                    description="batch payout 1",
                    to_bin="970422",
                    to_account_number="0123456789",
                    to_account_name="NGUYEN VAN A",
                    reference="FT-REF-1",
                    transaction_datetime="2025-12-12T09:00:00+07:00",
                    error_message=None,
                    error_code=None,
                    state="SUCCEEDED",
                ),
                PayoutTransaction(
                    id="txn-2",
                    reference_id="ref-2",
                    amount=3000,
                    description="batch payout 2",
                    to_bin="970422",
                    to_account_number="9999999999",
                    to_account_name=None,
                    reference=None,
                    transaction_datetime=None,
                    error_message="error message",
                    error_code="error code",
                    state="FAILED",
                ),
            ],
            category=["salary"],
            approval_state="PARTIAL_COMPLETED",
            created_at="2025-12-12T09:00:00+07:00",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v1/payouts/batch",
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

        result = client.payouts.batch.create(batch_request)

        assert result.id == "batch-id-partial"
        assert result.approval_state == "PARTIAL_COMPLETED"
        assert result.transactions[0].state == "SUCCEEDED"
        assert result.transactions[1].state == "FAILED"
        assert result.transactions[1].error_message == "error message"
        assert result.transactions[1].error_code == "error code"


class TestAsyncBatch:
    """Asynchronous tests for AsyncBatch."""

    @pytest.mark.asyncio
    async def test_create_batch_single_item(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test creating batch payout with single item."""
        batch_request = PayoutBatchRequest(
            reference_id="batch-ref-1",
            category=["salary"],
            validate_destination=True,
            payouts=[
                PayoutBatchItem(
                    reference_id="ref-1",
                    amount=2000,
                    description="batch payout",
                    to_bin="970422",
                    to_account_number="0123456789",
                )
            ],
        )

        mock_payout_response = Payout(
            id="batch-id",
            reference_id="batch-ref-1",
            transactions=[
                PayoutTransaction(
                    id="txn-id",
                    reference_id="ref-1",
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
            url=f"{BASE_URL}/v1/payouts/batch",
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

        result = await client.payouts.batch.create(batch_request)

        assert result.id == "batch-id"
        assert result.reference_id == "batch-ref-1"
        assert len(result.transactions) == 1
        assert result.transactions[0].state == "SUCCEEDED"
        assert result.approval_state == "COMPLETED"
        assert result.category == ["salary"]

    @pytest.mark.asyncio
    async def test_create_batch_multiple_items(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test creating batch payout with multiple items."""
        batch_request = PayoutBatchRequest(
            reference_id="batch-ref-multi",
            category=["salary", "bonus"],
            validate_destination=True,
            payouts=[
                PayoutBatchItem(
                    reference_id="ref-1",
                    amount=2000,
                    description="batch payout 1",
                    to_bin="970422",
                    to_account_number="0123456789",
                ),
                PayoutBatchItem(
                    reference_id="ref-2",
                    amount=3000,
                    description="batch payout 2",
                    to_bin="970422",
                    to_account_number="9876543210",
                ),
                PayoutBatchItem(
                    reference_id="ref-3",
                    amount=1500,
                    description="batch payout 3",
                    to_bin="970422",
                    to_account_number="1122334455",
                ),
            ],
        )

        mock_payout_response = Payout(
            id="batch-id-multi",
            reference_id="batch-ref-multi",
            transactions=[
                PayoutTransaction(
                    id="txn-1",
                    reference_id="ref-1",
                    amount=2000,
                    description="batch payout 1",
                    to_bin="970422",
                    to_account_number="0123456789",
                    to_account_name="NGUYEN VAN A",
                    reference="FT-REF-1",
                    transaction_datetime="2025-12-12T09:00:00+07:00",
                    error_message=None,
                    error_code=None,
                    state="SUCCEEDED",
                ),
                PayoutTransaction(
                    id="txn-2",
                    reference_id="ref-2",
                    amount=3000,
                    description="batch payout 2",
                    to_bin="970422",
                    to_account_number="9876543210",
                    to_account_name="TRAN THI B",
                    reference="FT-REF-2",
                    transaction_datetime="2025-12-12T09:00:00+07:00",
                    error_message=None,
                    error_code=None,
                    state="SUCCEEDED",
                ),
                PayoutTransaction(
                    id="txn-3",
                    reference_id="ref-3",
                    amount=1500,
                    description="batch payout 3",
                    to_bin="970422",
                    to_account_number="1122334455",
                    to_account_name="LE VAN C",
                    reference="FT-REF-3",
                    transaction_datetime="2025-12-12T09:00:00+07:00",
                    error_message=None,
                    error_code=None,
                    state="SUCCEEDED",
                ),
            ],
            category=["salary", "bonus"],
            approval_state="COMPLETED",
            created_at="2025-12-12T09:00:00+07:00",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v1/payouts/batch",
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

        result = await client.payouts.batch.create(batch_request)

        assert result.id == "batch-id-multi"
        assert result.reference_id == "batch-ref-multi"
        assert len(result.transactions) == 3
        assert result.category == ["salary", "bonus"]
        assert result.approval_state == "COMPLETED"

    @pytest.mark.asyncio
    async def test_create_batch_without_category(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test creating batch payout without category."""
        batch_request = PayoutBatchRequest(
            reference_id="batch-ref-no-cat",
            category=None,
            validate_destination=False,
            payouts=[
                PayoutBatchItem(
                    reference_id="ref-1",
                    amount=2000,
                    description="batch payout",
                    to_bin="970422",
                    to_account_number="0123456789",
                )
            ],
        )

        mock_payout_response = Payout(
            id="batch-id",
            reference_id="batch-ref-no-cat",
            transactions=[
                PayoutTransaction(
                    id="txn-id",
                    reference_id="ref-1",
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
            category=None,
            approval_state="COMPLETED",
            created_at="2025-12-12T09:00:00+07:00",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v1/payouts/batch",
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

        result = await client.payouts.batch.create(batch_request)

        assert result.id == "batch-id"
        assert result.reference_id == "batch-ref-no-cat"
        assert result.category is None

    @pytest.mark.asyncio
    async def test_create_batch_custom_idempotency_key(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test creating batch payout with custom idempotency key."""
        custom_idempotency_key = "custom-batch-uuid-12345"

        batch_request = PayoutBatchRequest(
            reference_id="batch-ref",
            category=["salary"],
            validate_destination=True,
            payouts=[
                PayoutBatchItem(
                    reference_id="ref-1",
                    amount=2000,
                    description="batch payout",
                    to_bin="970422",
                    to_account_number="0123456789",
                )
            ],
        )

        mock_payout_response = Payout(
            id="batch-id",
            reference_id="batch-ref",
            transactions=[
                PayoutTransaction(
                    id="txn-id",
                    reference_id="ref-1",
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
            url=f"{BASE_URL}/v1/payouts/batch",
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

        result = await client.payouts.batch.create(
            batch_request, idempotency_key=custom_idempotency_key
        )

        assert result.id == "batch-id"
        assert result.reference_id == "batch-ref"

        request = httpx_mock.get_request()
        assert request is not None
        assert request.headers["x-idempotency-key"] == custom_idempotency_key

    @pytest.mark.asyncio
    async def test_create_batch_partial_completed(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test creating batch payout with PARTIAL_COMPLETED state."""
        batch_request = PayoutBatchRequest(
            reference_id="batch-ref-partial",
            category=["salary"],
            validate_destination=True,
            payouts=[
                PayoutBatchItem(
                    reference_id="ref-1",
                    amount=2000,
                    description="batch payout 1",
                    to_bin="970422",
                    to_account_number="0123456789",
                ),
                PayoutBatchItem(
                    reference_id="ref-2",
                    amount=3000,
                    description="batch payout 2",
                    to_bin="970422",
                    to_account_number="9999999999",
                ),
            ],
        )

        mock_payout_response = Payout(
            id="batch-id-partial",
            reference_id="batch-ref-partial",
            transactions=[
                PayoutTransaction(
                    id="txn-1",
                    reference_id="ref-1",
                    amount=2000,
                    description="batch payout 1",
                    to_bin="970422",
                    to_account_number="0123456789",
                    to_account_name="NGUYEN VAN A",
                    reference="FT-REF-1",
                    transaction_datetime="2025-12-12T09:00:00+07:00",
                    error_message=None,
                    error_code=None,
                    state="SUCCEEDED",
                ),
                PayoutTransaction(
                    id="txn-2",
                    reference_id="ref-2",
                    amount=3000,
                    description="batch payout 2",
                    to_bin="970422",
                    to_account_number="9999999999",
                    to_account_name=None,
                    reference=None,
                    transaction_datetime=None,
                    error_message="error message",
                    error_code="error code",
                    state="FAILED",
                ),
            ],
            category=["salary"],
            approval_state="PARTIAL_COMPLETED",
            created_at="2025-12-12T09:00:00+07:00",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v1/payouts/batch",
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

        result = await client.payouts.batch.create(batch_request)

        assert result.id == "batch-id-partial"
        assert result.approval_state == "PARTIAL_COMPLETED"
        assert result.transactions[0].state == "SUCCEEDED"
        assert result.transactions[1].state == "FAILED"
        assert result.transactions[1].error_message == "error message"
        assert result.transactions[1].error_code == "error code"
