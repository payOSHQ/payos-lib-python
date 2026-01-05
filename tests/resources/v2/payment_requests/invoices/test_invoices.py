"""Tests for invoices resource."""

import pytest
from payos import AsyncPayOS, PayOS
from payos.types.v2 import InvoicesInfo, Invoice
from pytest_httpx import HTTPXMock

# Constants
CLIENT_ID = "test-client-id"
API_KEY = "test-api-key"
CHECKSUM_KEY = "test-checksum-key"
BASE_URL = "https://api-test.payos.vn"


class TestInvoices:
    """Synchronous tests for Invoices."""

    def test_get_by_payment_link_id_single(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test getting invoices by payment link ID with single invoice."""
        payment_link_id = "payment-link-id"
        mock_invoices_info = InvoicesInfo(
            invoices=[
                Invoice(
                    invoice_id="invoice-id",
                    invoice_number="INV-001",
                    issued_timestamp=1765504800,
                    issued_datetime="2025-12-12T02:00:00.000Z",
                    transaction_id="txn-id",
                    reservation_code="RES-CODE",
                    code_of_tax="TAX-CODE",
                ),
            ]
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{payment_link_id}/invoices",
            method="GET",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_invoices_info.model_dump(by_alias=True),
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

        result = client.payment_requests.invoices.get(payment_link_id)

        assert len(result.invoices) == 1
        assert result.invoices[0].invoice_number == "INV-001"

    def test_get_by_order_code(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test getting invoices by order code."""
        order_code = 12345
        mock_invoices_info = InvoicesInfo(
            invoices=[
                Invoice(
                    invoice_id="invoice-id",
                    invoice_number="INV-002",
                    issued_timestamp=1765504800,
                    issued_datetime="2025-12-12T02:00:00.000Z",
                    transaction_id="txn-id",
                    reservation_code="RES-CODE",
                    code_of_tax="TAX-CODE",
                ),
            ]
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{order_code}/invoices",
            method="GET",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_invoices_info.model_dump(by_alias=True),
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

        result = client.payment_requests.invoices.get(order_code)

        assert result.invoices[0].invoice_number == "INV-002"

    def test_get_multiple_invoices(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test getting multiple invoices."""
        payment_link_id = "payment-link-id"
        mock_invoices_info = InvoicesInfo(
            invoices=[
                Invoice(
                    invoice_id="invoice-id",
                    invoice_number="INV-001",
                    issued_timestamp=1765504800,
                    issued_datetime="2025-12-12T02:00:00.000Z",
                    transaction_id="txn-id",
                    reservation_code="RES-CODE",
                    code_of_tax="TAX-CODE",
                ),
                Invoice(
                    invoice_id="invoice-id",
                ),
            ]
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{payment_link_id}/invoices",
            method="GET",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_invoices_info.model_dump(by_alias=True),
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

        result = client.payment_requests.invoices.get(payment_link_id)

        assert len(result.invoices) == 2
        assert result.invoices[0].invoice_number == "INV-001"
        assert result.invoices[1].invoice_number is None

    def test_get_empty_invoices(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test getting empty invoices list."""
        payment_link_id = "payment-link-id"
        mock_invoices_info = InvoicesInfo(invoices=[])

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{payment_link_id}/invoices",
            method="GET",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_invoices_info.model_dump(by_alias=True),
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

        result = client.payment_requests.invoices.get(payment_link_id)

        assert len(result.invoices) == 0

    def test_download_by_payment_link_id(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test downloading invoice by payment link ID."""
        invoice_id = "invoice-id"
        payment_link_id = "payment-link-id"
        mock_pdf_data = b"mock-pdf-data"

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{payment_link_id}/invoices/{invoice_id}/download",
            method="GET",
            content=mock_pdf_data,
            status_code=200,
            headers={
                "Content-Type": "application/pdf",
                "Content-Disposition": 'attachment; filename="invoice.pdf"',
            },
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_sync)

        result = client.payment_requests.invoices.download(invoice_id, payment_link_id)

        assert result.data == mock_pdf_data
        assert result.content_type == "application/pdf"
        assert result.filename == "invoice.pdf"

    def test_download_by_order_code(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test downloading invoice by order code."""
        invoice_id = "invoice-id"
        order_code = 12345
        mock_pdf_data = b"mock-pdf-data"

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{order_code}/invoices/{invoice_id}/download",
            method="GET",
            content=mock_pdf_data,
            status_code=200,
            headers={
                "Content-Type": "application/pdf",
                "Content-Disposition": 'attachment; filename="invoice-12345.pdf"',
            },
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_sync)

        result = client.payment_requests.invoices.download(invoice_id, order_code)

        assert result.data == mock_pdf_data
        assert result.content_type == "application/pdf"
        assert result.filename == "invoice-12345.pdf"

    def test_download_different_content_type(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test downloading invoice with different content type."""
        invoice_id = "invoice-id"
        payment_link_id = "payment-link-id"
        mock_data = b"mock-data"

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{payment_link_id}/invoices/{invoice_id}/download",
            method="GET",
            content=mock_data,
            status_code=200,
            headers={
                "Content-Type": "application/octet-stream",
                "Content-Disposition": 'attachment; filename="document.bin"',
            },
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_sync)

        result = client.payment_requests.invoices.download(invoice_id, payment_link_id)

        assert result.content_type == "application/octet-stream"
        assert result.filename == "document.bin"

    def test_download_without_filename(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test downloading invoice without filename in header."""
        invoice_id = "invoice-id"
        payment_link_id = "payment-link-id"
        mock_pdf_data = b"mock-pdf-data"

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{payment_link_id}/invoices/{invoice_id}/download",
            method="GET",
            content=mock_pdf_data,
            status_code=200,
            headers={"Content-Type": "application/pdf"},
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_sync)

        result = client.payment_requests.invoices.download(invoice_id, payment_link_id)

        assert result.content_type == "application/pdf"
        assert result.filename == "download"


class TestAsyncInvoices:
    """Asynchronous tests for AsyncInvoices."""

    @pytest.mark.asyncio
    async def test_get_by_payment_link_id_single(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test getting invoices by payment link ID with single invoice."""
        payment_link_id = "payment-link-id"
        mock_invoices_info = InvoicesInfo(
            invoices=[
                Invoice(
                    invoice_id="invoice-id",
                    invoice_number="INV-001",
                    issued_timestamp=1765504800,
                    issued_datetime="2025-12-12T02:00:00.000Z",
                    transaction_id="txn-id",
                    reservation_code="RES-CODE",
                    code_of_tax="TAX-CODE",
                ),
            ]
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{payment_link_id}/invoices",
            method="GET",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_invoices_info.model_dump(by_alias=True),
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

        result = await client.payment_requests.invoices.get(payment_link_id)

        assert len(result.invoices) == 1
        assert result.invoices[0].invoice_number == "INV-001"

    @pytest.mark.asyncio
    async def test_get_by_order_code(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test getting invoices by order code."""
        order_code = 12345
        mock_invoices_info = InvoicesInfo(
            invoices=[
                Invoice(
                    invoice_id="invoice-id",
                    invoice_number="INV-002",
                    issued_timestamp=1765504800,
                    issued_datetime="2025-12-12T02:00:00.000Z",
                    transaction_id="txn-id",
                    reservation_code="RES-CODE",
                    code_of_tax="TAX-CODE",
                ),
            ]
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{order_code}/invoices",
            method="GET",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_invoices_info.model_dump(by_alias=True),
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

        result = await client.payment_requests.invoices.get(order_code)

        assert result.invoices[0].invoice_number == "INV-002"

    @pytest.mark.asyncio
    async def test_get_multiple_invoices(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test getting multiple invoices."""
        payment_link_id = "payment-link-id"
        mock_invoices_info = InvoicesInfo(
            invoices=[
                Invoice(
                    invoice_id="invoice-id",
                    invoice_number="INV-001",
                    issued_timestamp=1765504800,
                    issued_datetime="2025-12-12T02:00:00.000Z",
                    transaction_id="txn-id",
                    reservation_code="RES-CODE",
                    code_of_tax="TAX-CODE",
                ),
                Invoice(
                    invoice_id="invoice-id",
                ),
            ]
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{payment_link_id}/invoices",
            method="GET",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_invoices_info.model_dump(by_alias=True),
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

        result = await client.payment_requests.invoices.get(payment_link_id)

        assert len(result.invoices) == 2
        assert result.invoices[0].invoice_number == "INV-001"
        assert result.invoices[1].invoice_number is None

    @pytest.mark.asyncio
    async def test_get_empty_invoices(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test getting empty invoices list."""
        payment_link_id = "payment-link-id"
        mock_invoices_info = InvoicesInfo(invoices=[])

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{payment_link_id}/invoices",
            method="GET",
            json={
                "code": "00",
                "desc": "success",
                "data": mock_invoices_info.model_dump(by_alias=True),
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

        result = await client.payment_requests.invoices.get(payment_link_id)

        assert len(result.invoices) == 0

    @pytest.mark.asyncio
    async def test_download_by_payment_link_id(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test downloading invoice by payment link ID."""
        invoice_id = "invoice-id"
        payment_link_id = "payment-link-id"
        mock_pdf_data = b"mock-pdf-data"

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{payment_link_id}/invoices/{invoice_id}/download",
            method="GET",
            content=mock_pdf_data,
            status_code=200,
            headers={
                "Content-Type": "application/pdf",
                "Content-Disposition": 'attachment; filename="invoice.pdf"',
            },
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_async)

        result = await client.payment_requests.invoices.download(invoice_id, payment_link_id)

        assert result.data == mock_pdf_data
        assert result.content_type == "application/pdf"
        assert result.filename == "invoice.pdf"

    @pytest.mark.asyncio
    async def test_download_by_order_code(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test downloading invoice by order code."""
        invoice_id = "invoice-id"
        order_code = 12345
        mock_pdf_data = b"mock-pdf-data"

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{order_code}/invoices/{invoice_id}/download",
            method="GET",
            content=mock_pdf_data,
            status_code=200,
            headers={
                "Content-Type": "application/pdf",
                "Content-Disposition": 'attachment; filename="invoice-12345.pdf"',
            },
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_async)

        result = await client.payment_requests.invoices.download(invoice_id, order_code)

        assert result.data == mock_pdf_data
        assert result.content_type == "application/pdf"
        assert result.filename == "invoice-12345.pdf"

    @pytest.mark.asyncio
    async def test_download_different_content_type(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test downloading invoice with different content type."""
        invoice_id = "invoice-id"
        payment_link_id = "payment-link-id"
        mock_data = b"mock-data"

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{payment_link_id}/invoices/{invoice_id}/download",
            method="GET",
            content=mock_data,
            status_code=200,
            headers={
                "Content-Type": "application/octet-stream",
                "Content-Disposition": 'attachment; filename="document.bin"',
            },
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_async)

        result = await client.payment_requests.invoices.download(invoice_id, payment_link_id)

        assert result.content_type == "application/octet-stream"
        assert result.filename == "document.bin"

    @pytest.mark.asyncio
    async def test_download_without_filename(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test downloading invoice without filename in header."""
        invoice_id = "invoice-id"
        payment_link_id = "payment-link-id"
        mock_pdf_data = b"mock-pdf-data"

        httpx_mock.add_response(
            url=f"{BASE_URL}/v2/payment-requests/{payment_link_id}/invoices/{invoice_id}/download",
            method="GET",
            content=mock_pdf_data,
            status_code=200,
            headers={"Content-Type": "application/pdf"},
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_async)

        result = await client.payment_requests.invoices.download(invoice_id, payment_link_id)

        assert result.content_type == "application/pdf"
        assert result.filename == "download"
