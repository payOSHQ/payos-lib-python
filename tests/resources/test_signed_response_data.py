"""Tests for body-signed response data validated through the public clients."""

import copy
import json
from typing import Any

import pytest
from pytest_httpx import HTTPXMock

from payos import AsyncPayOS, InvalidSignatureError, PayOS
from payos._crypto import CryptoProvider
from payos.types.v2 import CreatePaymentLinkRequest

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")

CLIENT_ID = "test-client-id"
API_KEY = "test-api-key"
CHECKSUM_KEY = "test-checksum-key"
BASE_URL = "https://api-test.payos.vn"
PAYMENT_LINK_ID = "0a3b8a2d5c1e4f6a9b7c0d1e2f3a4b5c"

PAYMENT_LINK = {
    "id": PAYMENT_LINK_ID,
    "orderCode": 1730530123,
    "amount": 15000,
    "amountPaid": 15000,
    "amountRemaining": 0,
    "status": "PAID",
    "createdAt": "2026-11-02T09:15:23+07:00",
    "transactions": [
        {
            "reference": "FT26306123456789",
            "amount": 15000,
            "accountNumber": "0123456789",
            "description": "CSPNZP7T3E5 Thanh toan don hang 1730530123",
            "transactionDateTime": "2026-11-02T09:16:01+07:00",
            "virtualAccountName": None,
            "virtualAccountNumber": None,
            "counterAccountBankId": "970422",
            "counterAccountBankName": "MB Bank",
            "counterAccountName": "NGUYEN VAN A",
            "counterAccountNumber": "9876543210",
        }
    ],
    "cancellationReason": None,
    "canceledAt": None,
}

CREATED_PAYMENT_LINK = {
    "bin": "970422",
    "accountNumber": "0123456789",
    "accountName": "NGUYEN VAN A",
    "amount": 15000,
    "description": "Thanh toan don hang",
    "orderCode": 1730530123,
    "currency": "VND",
    "paymentLinkId": PAYMENT_LINK_ID,
    "status": "PENDING",
    "expiredAt": 1730533723,
    "checkoutUrl": f"https://pay.payos.vn/web/{PAYMENT_LINK_ID}",
    "qrCode": "00020101021238570010A000000727012700069704220113VQRQ00001234560208QRIBFTTA5303704540415000",
}

INVOICES = {
    "invoices": [
        {
            "invoiceId": "6a7b8c9d-0e1f-4a2b-8c3d-4e5f6a7b8c9d",
            "invoiceNumber": "00000123",
            "issuedTimestamp": 1730530200,
            "issuedDatetime": "2026-11-02T02:10:00.000Z",
            "transactionId": "FT26306123456789",
            "reservationCode": "C26TAA123",
            "codeOfTax": "M1-26-ABCDE-00000000123",
        }
    ]
}


def _with(base: dict[str, Any], **changes: Any) -> dict[str, Any]:
    data = copy.deepcopy(base)
    data.update(changes)
    return data


def _with_transaction(**changes: Any) -> dict[str, Any]:
    data = copy.deepcopy(PAYMENT_LINK)
    data["transactions"][0].update(changes)
    return data


# (data, expected message after "Invalid response data: ")
REJECTED_PAYMENT_LINKS = [
    pytest.param(
        _with(PAYMENT_LINK, cancellationReason="none&amountPaid=0"),
        '"cancellationReason" must not contain a "&key=" sequence',
        id="ampersand-key sequence in top-level string",
    ),
    pytest.param(
        _with_transaction(description="CSPNZP7T3E5&status=PAID"),
        '"transactions[0].description" must not contain a "&key=" sequence',
        id="ampersand-key sequence in list item string",
    ),
    pytest.param(
        {**PAYMENT_LINK, "order-code": 1},
        'unsupported key "order-code"',
        id="key with hyphen",
    ),
    pytest.param(
        {**PAYMENT_LINK, "__proto__": 1},
        'unsupported key "__proto__"',
        id="proto key",
    ),
    pytest.param(
        _with_transaction(**{"bank id": "970422"}),
        'unsupported key "transactions[0].bank id"',
        id="list item key with space",
    ),
    pytest.param(
        _with(PAYMENT_LINK, canceledAt={"at": "2026-11-02"}),
        '"canceledAt" has an unsupported type',
        id="nested object",
    ),
    pytest.param(
        _with_transaction(counterAccountBankName={"name": "MB Bank"}),
        '"transactions[0].counterAccountBankName" has an unsupported type',
        id="object nested in list item",
    ),
    pytest.param(
        _with(PAYMENT_LINK, transactions=[["FT26306123456789", 15000]]),
        '"transactions[0]" has an unsupported type',
        id="list nested in list",
    ),
    pytest.param(
        _with(PAYMENT_LINK, amount=float("nan")),
        '"amount" must be a finite number within the safe integer range',
        id="nan",
    ),
    pytest.param(
        _with(PAYMENT_LINK, amount=float("inf")),
        '"amount" must be a finite number within the safe integer range',
        id="infinity",
    ),
    pytest.param(
        _with(PAYMENT_LINK, amount=1e300),
        '"amount" must be a finite number within the safe integer range',
        id="float beyond safe integer range",
    ),
    pytest.param(
        _with(PAYMENT_LINK, orderCode=2**53),
        '"orderCode" must be a safe integer',
        id="unsafe integer",
    ),
    pytest.param(
        _with_transaction(amount=-(2**53)),
        '"transactions[0].amount" must be a safe integer',
        id="unsafe negative integer in list item",
    ),
]


def _sign(data: Any) -> str:
    signature = CryptoProvider().create_signature_from_object(data, CHECKSUM_KEY)
    assert signature
    return signature


def _signed_body(data: Any) -> bytes:
    """Serialise a success envelope whose signature is computed over ``data`` with the checksum key."""
    return json.dumps(
        {"code": "00", "desc": "success", "data": data, "signature": _sign(data)}
    ).encode()


def _add_signed_response(httpx_mock: HTTPXMock, method: str, path: str, data: Any) -> None:
    httpx_mock.add_response(
        method=method,
        url=f"{BASE_URL}{path}",
        content=_signed_body(data),
        headers={"content-type": "application/json"},
    )


def _payment_request() -> CreatePaymentLinkRequest:
    return CreatePaymentLinkRequest(
        order_code=1730530123,
        amount=15000,
        description="Thanh toan don hang",
        cancel_url="https://merchant.example/cancel",
        return_url="https://merchant.example/return",
    )


def _sync_client() -> PayOS:
    return PayOS(
        client_id=CLIENT_ID,
        api_key=API_KEY,
        checksum_key=CHECKSUM_KEY,
        base_url=BASE_URL,
        max_retries=0,
    )


def _async_client() -> AsyncPayOS:
    return AsyncPayOS(
        client_id=CLIENT_ID,
        api_key=API_KEY,
        checksum_key=CHECKSUM_KEY,
        base_url=BASE_URL,
        max_retries=0,
    )


class TestSignedResponseData:
    """Body-signed response data handled by the sync client."""

    def test_signed_payment_link_is_accepted(self, httpx_mock: HTTPXMock):
        """Test a realistic payment link with a correct signature is returned."""
        _add_signed_response(
            httpx_mock, "GET", f"/v2/payment-requests/{PAYMENT_LINK_ID}", PAYMENT_LINK
        )

        result = _sync_client().payment_requests.get(PAYMENT_LINK_ID)

        assert result.id == PAYMENT_LINK_ID
        assert result.status == "PAID"
        assert result.transactions[0].reference == "FT26306123456789"

    def test_signed_created_payment_link_is_accepted(self, httpx_mock: HTTPXMock):
        """Test a realistic created payment link with a correct signature is returned."""
        _add_signed_response(httpx_mock, "POST", "/v2/payment-requests", CREATED_PAYMENT_LINK)

        result = _sync_client().payment_requests.create(_payment_request())

        assert result.payment_link_id == PAYMENT_LINK_ID
        assert result.checkout_url == CREATED_PAYMENT_LINK["checkoutUrl"]

    def test_signed_cancelled_payment_link_is_accepted(self, httpx_mock: HTTPXMock):
        """Test a cancelled payment link with a correct signature is returned."""
        data = _with(
            PAYMENT_LINK,
            status="CANCELLED",
            cancellationReason="Khach hang huy don",
            canceledAt="2026-11-02T09:20:00+07:00",
        )
        _add_signed_response(
            httpx_mock, "POST", f"/v2/payment-requests/{PAYMENT_LINK_ID}/cancel", data
        )

        result = _sync_client().payment_requests.cancel(PAYMENT_LINK_ID, "Khach hang huy don")

        assert result.status == "CANCELLED"
        assert result.cancellation_reason == "Khach hang huy don"

    def test_signed_invoices_are_accepted(self, httpx_mock: HTTPXMock):
        """Test realistic invoices with a correct signature are returned."""
        _add_signed_response(
            httpx_mock, "GET", f"/v2/payment-requests/{PAYMENT_LINK_ID}/invoices", INVOICES
        )

        result = _sync_client().payment_requests.invoices.get(PAYMENT_LINK_ID)

        assert result.invoices[0].invoice_number == "00000123"

    def test_signed_payment_link_is_accepted_by_legacy_method(self, httpx_mock: HTTPXMock):
        """Test the legacy getter returns a realistic payment link with a correct signature."""
        _add_signed_response(
            httpx_mock, "GET", f"/v2/payment-requests/{PAYMENT_LINK_ID}", PAYMENT_LINK
        )

        result = _sync_client().getPaymentLinkInformation(PAYMENT_LINK_ID)

        assert result.id == PAYMENT_LINK_ID
        assert result.transactions[0].reference == "FT26306123456789"

    @pytest.mark.parametrize(("data", "reason"), REJECTED_PAYMENT_LINKS)
    def test_signed_payment_link_with_unsupported_data_is_rejected(
        self, httpx_mock: HTTPXMock, data: dict[str, Any], reason: str
    ):
        """Test data is validated before the signature, even when the signature matches it."""
        _add_signed_response(httpx_mock, "GET", f"/v2/payment-requests/{PAYMENT_LINK_ID}", data)

        with pytest.raises(InvalidSignatureError) as excinfo:
            _sync_client().payment_requests.get(PAYMENT_LINK_ID)

        assert str(excinfo.value) == f"Invalid response data: {reason}"

    def test_non_object_data_is_rejected(self, httpx_mock: HTTPXMock):
        """Test data that is not a JSON object is rejected."""
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE_URL}/v2/payment-requests/{PAYMENT_LINK_ID}",
            json={"code": "00", "desc": "success", "data": [PAYMENT_LINK], "signature": "0" * 64},
        )

        with pytest.raises(InvalidSignatureError) as excinfo:
            _sync_client().payment_requests.get(PAYMENT_LINK_ID)

        assert str(excinfo.value) == "Invalid response data: data must be a JSON object"

    def test_signed_created_payment_link_with_ampersand_key_is_rejected(
        self, httpx_mock: HTTPXMock
    ):
        """Test an ampersand-key sequence is rejected in a created payment link."""
        data = _with(CREATED_PAYMENT_LINK, accountName="NGUYEN VAN A&bin=970422")
        _add_signed_response(httpx_mock, "POST", "/v2/payment-requests", data)

        with pytest.raises(InvalidSignatureError) as excinfo:
            _sync_client().payment_requests.create(_payment_request())

        assert str(excinfo.value) == (
            'Invalid response data: "accountName" must not contain a "&key=" sequence'
        )

    def test_signed_invoices_with_ampersand_key_are_rejected(self, httpx_mock: HTTPXMock):
        """Test an ampersand-key sequence is rejected inside an invoice list item."""
        data = copy.deepcopy(INVOICES)
        data["invoices"][0]["invoiceNumber"] = "00000123&codeOfTax=X"
        _add_signed_response(
            httpx_mock, "GET", f"/v2/payment-requests/{PAYMENT_LINK_ID}/invoices", data
        )

        with pytest.raises(InvalidSignatureError) as excinfo:
            _sync_client().payment_requests.invoices.get(PAYMENT_LINK_ID)

        assert str(excinfo.value) == (
            'Invalid response data: "invoices[0].invoiceNumber" must not contain a "&key=" sequence'
        )

    @pytest.mark.parametrize("method", ["getPaymentLinkInformation", "cancelPaymentLink"])
    def test_legacy_methods_reject_ampersand_key_sequence(self, httpx_mock: HTTPXMock, method: str):
        """Test the legacy methods validate signed data before the signature."""
        path = f"/v2/payment-requests/{PAYMENT_LINK_ID}"
        if method == "cancelPaymentLink":
            path += "/cancel"
        data = _with_transaction(description="CSPNZP7T3E5&status=PAID")
        _add_signed_response(
            httpx_mock, "POST" if method == "cancelPaymentLink" else "GET", path, data
        )

        with pytest.raises(InvalidSignatureError) as excinfo:
            getattr(_sync_client(), method)(PAYMENT_LINK_ID)

        assert str(excinfo.value) == (
            'Invalid response data: "transactions[0].description" must not contain a "&key=" sequence'
        )


class TestAsyncSignedResponseData:
    """Body-signed response data handled by the async client."""

    async def test_signed_payment_link_is_accepted(self, httpx_mock: HTTPXMock):
        """Test a realistic payment link with a correct signature is returned."""
        _add_signed_response(
            httpx_mock, "GET", f"/v2/payment-requests/{PAYMENT_LINK_ID}", PAYMENT_LINK
        )

        result = await _async_client().payment_requests.get(PAYMENT_LINK_ID)

        assert result.id == PAYMENT_LINK_ID
        assert result.transactions[0].reference == "FT26306123456789"

    async def test_signed_invoices_are_accepted(self, httpx_mock: HTTPXMock):
        """Test realistic invoices with a correct signature are returned."""
        _add_signed_response(
            httpx_mock, "GET", f"/v2/payment-requests/{PAYMENT_LINK_ID}/invoices", INVOICES
        )

        result = await _async_client().payment_requests.invoices.get(PAYMENT_LINK_ID)

        assert result.invoices[0].invoice_number == "00000123"

    async def test_signed_payment_link_is_accepted_by_legacy_method(self, httpx_mock: HTTPXMock):
        """Test the legacy getter returns a realistic payment link with a correct signature."""
        _add_signed_response(
            httpx_mock, "GET", f"/v2/payment-requests/{PAYMENT_LINK_ID}", PAYMENT_LINK
        )

        result = await _async_client().getPaymentLinkInformation(PAYMENT_LINK_ID)

        assert result.id == PAYMENT_LINK_ID

    @pytest.mark.parametrize(("data", "reason"), REJECTED_PAYMENT_LINKS)
    async def test_signed_payment_link_with_unsupported_data_is_rejected(
        self, httpx_mock: HTTPXMock, data: dict[str, Any], reason: str
    ):
        """Test data is validated before the signature, even when the signature matches it."""
        _add_signed_response(httpx_mock, "GET", f"/v2/payment-requests/{PAYMENT_LINK_ID}", data)

        with pytest.raises(InvalidSignatureError) as excinfo:
            await _async_client().payment_requests.get(PAYMENT_LINK_ID)

        assert str(excinfo.value) == f"Invalid response data: {reason}"

    @pytest.mark.parametrize("method", ["getPaymentLinkInformation", "cancelPaymentLink"])
    async def test_legacy_methods_reject_ampersand_key_sequence(
        self, httpx_mock: HTTPXMock, method: str
    ):
        """Test the legacy methods validate signed data before the signature."""
        path = f"/v2/payment-requests/{PAYMENT_LINK_ID}"
        if method == "cancelPaymentLink":
            path += "/cancel"
        data = _with_transaction(description="CSPNZP7T3E5&status=PAID")
        _add_signed_response(
            httpx_mock, "POST" if method == "cancelPaymentLink" else "GET", path, data
        )

        with pytest.raises(InvalidSignatureError) as excinfo:
            await getattr(_async_client(), method)(PAYMENT_LINK_ID)

        assert str(excinfo.value) == (
            'Invalid response data: "transactions[0].description" must not contain a "&key=" sequence'
        )
