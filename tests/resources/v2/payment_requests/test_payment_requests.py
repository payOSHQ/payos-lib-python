"""Tests for payment requests resource."""

import pytest
from pytest_httpx import HTTPXMock
from payos import AsyncPayOS, PayOS
from payos.types.v2 import (
    CreatePaymentLinkRequest,
    CreatePaymentLinkResponse,
    PaymentLink,
    ItemData,
    InvoiceRequest,
    Transaction,
)

# Constants
CLIENT_ID = "test-client-id"
API_KEY = "test-api-key"
CHECKSUM_KEY = "test-checksum-key"
BASE_URL = "https://api-test.payos.vn"


class TestPaymentRequests:
    """Synchronous tests for PaymentRequests."""

    def test_create_minimal_fields(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test creating payment link with minimal required fields."""
        payment_request = CreatePaymentLinkRequest(
            order_code=12345,
            amount=2000,
            description="Test payment",
            cancel_url="http://localhost/cancel",
            return_url="http://localhost/return",
        )

        mock_response = CreatePaymentLinkResponse(
            bin="970422",
            account_number="0123456789",
            account_name="NGUYEN VAN A",
            amount=2000,
            description="Test payment",
            order_code=12345,
            currency="VND",
            payment_link_id="payment-link-id",
            status="PENDING",
            checkout_url="https://pay.payos.vn/payment-link-id",
            qr_code="qrcode",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests",
            method="POST",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_response.model_dump(by_alias=True),
                "signature": "mock-signature",
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

        result = client.payment_requests.create(payment_request)

        assert result.payment_link_id == "payment-link-id"
        assert result.status == "PENDING"
        assert result.amount == 2000
        assert result.order_code == 12345

    def test_create_full_fields(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test creating payment link with full fields including items and invoice."""
        payment_request = CreatePaymentLinkRequest(
            order_code=12345,
            amount=3300,
            description="Full fields payment",
            cancel_url="http://localhost/cancel",
            return_url="http://localhost/return",
            buyer_name="buyer name",
            buyer_company_name="company name",
            buyer_tax_code="0316794479",
            buyer_email="buyer@email.com",
            buyer_phone="0123456789",
            buyer_address="buyer address",
            items=[
                ItemData(name="product 1", quantity=1, price=1000, unit="piece", tax_percentage=10),
                ItemData(name="product 2", quantity=1, price=2000, unit="piece", tax_percentage=10),
            ],
            invoice=InvoiceRequest(buyer_not_get_invoice=False, tax_percentage=10),
        )

        mock_response = CreatePaymentLinkResponse(
            bin="970422",
            account_number="0123456789",
            account_name="NGUYEN VAN A",
            amount=3300,
            description="Full fields payment",
            order_code=12345,
            currency="VND",
            payment_link_id="payment-link-id",
            status="PENDING",
            checkout_url="https://pay.payos.vn/payment-link-id",
            qr_code="qrcode",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests",
            method="POST",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_response.model_dump(by_alias=True),
                "signature": "mock-signature",
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

        result = client.payment_requests.create(payment_request)

        assert result.payment_link_id == "payment-link-id"
        assert result.amount == 3300

    def test_get_by_payment_link_id(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test getting payment link by payment link ID."""
        payment_link_id = "payment-link-id"
        mock_payment_link = PaymentLink(
            id=payment_link_id,
            order_code=12345,
            amount=2000,
            amount_paid=2000,
            amount_remaining=0,
            status="PAID",
            created_at="2025-12-12T09:00:00+07:00",
            transactions=[
                Transaction(
                    reference="FT-REFERENCE",
                    amount=2000,
                    account_number="0123456789",
                    description="Payment",
                    transaction_date_time="2025-12-12T09:00:00+07:00",
                    virtual_account_name=None,
                    virtual_account_number=None,
                    counter_account_bank_id="01202001",
                    counter_account_bank_name=None,
                    counter_account_name="NGUYEN VAN A",
                    counter_account_number="9876543210",
                )
            ],
            cancellation_reason=None,
            canceled_at=None,
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{payment_link_id}",
            method="GET",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_payment_link.model_dump(by_alias=True),
                "signature": "mock-signature",
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

        result = client.payment_requests.get(payment_link_id)

        assert result.id == payment_link_id
        assert result.status == "PAID"
        assert len(result.transactions) == 1

    def test_get_by_order_code(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test getting payment link by order code."""
        order_code = 12345
        mock_payment_link = PaymentLink(
            id="payment-link-id",
            order_code=order_code,
            amount=2000,
            amount_paid=0,
            amount_remaining=2000,
            status="PENDING",
            created_at="2025-12-12T09:00:00+07:00",
            transactions=[],
            cancellation_reason=None,
            canceled_at=None,
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{order_code}",
            method="GET",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_payment_link.model_dump(by_alias=True),
                "signature": "mock-signature",
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

        result = client.payment_requests.get(order_code)

        assert result.order_code == order_code
        assert result.status == "PENDING"

    def test_get_expired_status(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test getting payment link with EXPIRED status."""
        payment_link_id = "expired-link"
        mock_payment_link = PaymentLink(
            id=payment_link_id,
            order_code=12345,
            amount=2000,
            amount_paid=0,
            amount_remaining=2000,
            status="EXPIRED",
            created_at="2025-12-12T09:00:00+07:00",
            transactions=[],
            cancellation_reason=None,
            canceled_at=None,
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{payment_link_id}",
            method="GET",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_payment_link.model_dump(by_alias=True),
                "signature": "mock-signature",
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

        result = client.payment_requests.get(payment_link_id)

        assert result.status == "EXPIRED"

    def test_cancel_by_id_without_reason(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test canceling payment link by ID without cancellation reason."""
        payment_link_id = "payment-link-id"
        mock_cancelled_link = PaymentLink(
            id=payment_link_id,
            order_code=12345,
            amount=2000,
            amount_paid=0,
            amount_remaining=2000,
            status="CANCELLED",
            created_at="2025-12-12T09:00:00+07:00",
            transactions=[],
            cancellation_reason=None,
            canceled_at="2025-12-12T10:00:00+07:00",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{payment_link_id}/cancel",
            method="POST",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_cancelled_link.model_dump(by_alias=True),
                "signature": "mock-signature",
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

        result = client.payment_requests.cancel(payment_link_id)

        assert result.status == "CANCELLED"
        assert result.cancellation_reason is None

    def test_cancel_by_id_with_reason(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test canceling payment link by ID with cancellation reason."""
        payment_link_id = "payment-link-id"
        cancellation_reason = "Customer requested cancellation"
        mock_cancelled_link = PaymentLink(
            id=payment_link_id,
            order_code=12345,
            amount=2000,
            amount_paid=0,
            amount_remaining=2000,
            status="CANCELLED",
            created_at="2025-12-12T09:00:00+07:00",
            transactions=[],
            cancellation_reason=cancellation_reason,
            canceled_at="2025-12-12T10:00:00+07:00",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{payment_link_id}/cancel",
            method="POST",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_cancelled_link.model_dump(by_alias=True),
                "signature": "mock-signature",
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

        result = client.payment_requests.cancel(payment_link_id, cancellation_reason)

        assert result.cancellation_reason == cancellation_reason

    def test_cancel_by_order_code(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test canceling payment link by order code."""
        order_code = 12345
        mock_cancelled_link = PaymentLink(
            id="payment-link-id",
            order_code=order_code,
            amount=2000,
            amount_paid=0,
            amount_remaining=2000,
            status="CANCELLED",
            created_at="2025-12-12T09:00:00+07:00",
            transactions=[],
            cancellation_reason=None,
            canceled_at="2025-12-12T10:00:00+07:00",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{order_code}/cancel",
            method="POST",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_cancelled_link.model_dump(by_alias=True),
                "signature": "mock-signature",
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

        result = client.payment_requests.cancel(order_code)

        assert result.order_code == order_code


class TestAsyncPaymentRequests:
    """Asynchronous tests for AsyncPaymentRequests."""

    @pytest.mark.asyncio
    async def test_create_minimal_fields(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test creating payment link with minimal required fields."""
        payment_request = CreatePaymentLinkRequest(
            order_code=12345,
            amount=2000,
            description="Test payment",
            cancel_url="http://localhost/cancel",
            return_url="http://localhost/return",
        )

        mock_response = CreatePaymentLinkResponse(
            bin="970422",
            account_number="0123456789",
            account_name="NGUYEN VAN A",
            amount=2000,
            description="Test payment",
            order_code=12345,
            currency="VND",
            payment_link_id="payment-link-id",
            status="PENDING",
            checkout_url="https://pay.payos.vn/payment-link-id",
            qr_code="qrcode",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests",
            method="POST",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_response.model_dump(by_alias=True),
                "signature": "mock-signature",
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

        result = await client.payment_requests.create(payment_request)

        assert result.payment_link_id == "payment-link-id"
        assert result.status == "PENDING"
        assert result.amount == 2000
        assert result.order_code == 12345

    @pytest.mark.asyncio
    async def test_create_full_fields(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test creating payment link with full fields including items and invoice."""
        payment_request = CreatePaymentLinkRequest(
            order_code=12345,
            amount=3300,
            description="Full fields payment",
            cancel_url="http://localhost/cancel",
            return_url="http://localhost/return",
            buyer_name="buyer name",
            buyer_company_name="company name",
            buyer_tax_code="0316794479",
            buyer_email="buyer@email.com",
            buyer_phone="0123456789",
            buyer_address="buyer address",
            items=[
                ItemData(name="product 1", quantity=1, price=1000, unit="piece", tax_percentage=10),
                ItemData(name="product 2", quantity=1, price=2000, unit="piece", tax_percentage=10),
            ],
            invoice=InvoiceRequest(buyer_not_get_invoice=False, tax_percentage=10),
        )

        mock_response = CreatePaymentLinkResponse(
            bin="970422",
            account_number="0123456789",
            account_name="NGUYEN VAN A",
            amount=3300,
            description="Full fields payment",
            order_code=12345,
            currency="VND",
            payment_link_id="payment-link-id",
            status="PENDING",
            checkout_url="https://pay.payos.vn/payment-link-id",
            qr_code="qrcode",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests",
            method="POST",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_response.model_dump(by_alias=True),
                "signature": "mock-signature",
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

        result = await client.payment_requests.create(payment_request)

        assert result.payment_link_id == "payment-link-id"
        assert result.amount == 3300

    @pytest.mark.asyncio
    async def test_get_by_payment_link_id(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test getting payment link by payment link ID."""
        payment_link_id = "payment-link-id"
        mock_payment_link = PaymentLink(
            id=payment_link_id,
            order_code=12345,
            amount=2000,
            amount_paid=2000,
            amount_remaining=0,
            status="PAID",
            created_at="2025-12-12T09:00:00+07:00",
            transactions=[
                Transaction(
                    reference="FT-REFERENCE",
                    amount=2000,
                    account_number="0123456789",
                    description="Payment",
                    transaction_date_time="2025-12-12T09:00:00+07:00",
                    virtual_account_name=None,
                    virtual_account_number=None,
                    counter_account_bank_id="01202001",
                    counter_account_bank_name=None,
                    counter_account_name="NGUYEN VAN A",
                    counter_account_number="9876543210",
                )
            ],
            cancellation_reason=None,
            canceled_at=None,
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{payment_link_id}",
            method="GET",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_payment_link.model_dump(by_alias=True),
                "signature": "mock-signature",
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

        result = await client.payment_requests.get(payment_link_id)

        assert result.id == payment_link_id
        assert result.status == "PAID"
        assert len(result.transactions) == 1

    @pytest.mark.asyncio
    async def test_get_by_order_code(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test getting payment link by order code."""
        order_code = 12345
        mock_payment_link = PaymentLink(
            id="payment-link-id",
            order_code=order_code,
            amount=2000,
            amount_paid=0,
            amount_remaining=2000,
            status="PENDING",
            created_at="2025-12-12T09:00:00+07:00",
            transactions=[],
            cancellation_reason=None,
            canceled_at=None,
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{order_code}",
            method="GET",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_payment_link.model_dump(by_alias=True),
                "signature": "mock-signature",
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

        result = await client.payment_requests.get(order_code)

        assert result.order_code == order_code
        assert result.status == "PENDING"

    @pytest.mark.asyncio
    async def test_get_expired_status(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test getting payment link with EXPIRED status."""
        payment_link_id = "expired-link"
        mock_payment_link = PaymentLink(
            id=payment_link_id,
            order_code=12345,
            amount=2000,
            amount_paid=0,
            amount_remaining=2000,
            status="EXPIRED",
            created_at="2025-12-12T09:00:00+07:00",
            transactions=[],
            cancellation_reason=None,
            canceled_at=None,
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{payment_link_id}",
            method="GET",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_payment_link.model_dump(by_alias=True),
                "signature": "mock-signature",
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

        result = await client.payment_requests.get(payment_link_id)

        assert result.status == "EXPIRED"

    @pytest.mark.asyncio
    async def test_cancel_by_id_without_reason(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test canceling payment link by ID without cancellation reason."""
        payment_link_id = "payment-link-id"
        mock_cancelled_link = PaymentLink(
            id=payment_link_id,
            order_code=12345,
            amount=2000,
            amount_paid=0,
            amount_remaining=2000,
            status="CANCELLED",
            created_at="2025-12-12T09:00:00+07:00",
            transactions=[],
            cancellation_reason=None,
            canceled_at="2025-12-12T10:00:00+07:00",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{payment_link_id}/cancel",
            method="POST",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_cancelled_link.model_dump(by_alias=True),
                "signature": "mock-signature",
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

        result = await client.payment_requests.cancel(payment_link_id)

        assert result.status == "CANCELLED"
        assert result.cancellation_reason is None

    @pytest.mark.asyncio
    async def test_cancel_by_id_with_reason(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test canceling payment link by ID with cancellation reason."""
        payment_link_id = "payment-link-id"
        cancellation_reason = "Customer requested cancellation"
        mock_cancelled_link = PaymentLink(
            id=payment_link_id,
            order_code=12345,
            amount=2000,
            amount_paid=0,
            amount_remaining=2000,
            status="CANCELLED",
            created_at="2025-12-12T09:00:00+07:00",
            transactions=[],
            cancellation_reason=cancellation_reason,
            canceled_at="2025-12-12T10:00:00+07:00",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{payment_link_id}/cancel",
            method="POST",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_cancelled_link.model_dump(by_alias=True),
                "signature": "mock-signature",
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

        result = await client.payment_requests.cancel(payment_link_id, cancellation_reason)

        assert result.cancellation_reason == cancellation_reason

    @pytest.mark.asyncio
    async def test_cancel_by_order_code(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test canceling payment link by order code."""
        order_code = 12345
        mock_cancelled_link = PaymentLink(
            id="payment-link-id",
            order_code=order_code,
            amount=2000,
            amount_paid=0,
            amount_remaining=2000,
            status="CANCELLED",
            created_at="2025-12-12T09:00:00+07:00",
            transactions=[],
            cancellation_reason=None,
            canceled_at="2025-12-12T10:00:00+07:00",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{order_code}/cancel",
            method="POST",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_cancelled_link.model_dump(by_alias=True),
                "signature": "mock-signature",
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

        result = await client.payment_requests.cancel(order_code)

        assert result.order_code == order_code
