"""Tests for identifiers interpolated into API paths through the public clients."""

import inspect
import warnings
from typing import Any, Callable

import pytest
from pytest_httpx import HTTPXMock

from payos import APIError, AsyncPayOS, PayOS, PayOSError

with warnings.catch_warnings():
    warnings.simplefilter("ignore", DeprecationWarning)
    from payos.custom_error import PayOSError as LegacyPayOSError

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")

CLIENT_ID = "test-client-id"
API_KEY = "test-api-key"
CHECKSUM_KEY = "test-checksum-key"
BASE_URL = "https://api-test.payos.vn"

# (call site, call, expected raw path template, parameter name, legacy)
CallSite = tuple[str, Callable[[Any, Any], Any], str, str, bool]

CALL_SITES: list[CallSite] = [
    (
        "payment_requests.get",
        lambda client, value: client.payment_requests.get(value),
        "/v2/payment-requests/{}",
        "id",
        False,
    ),
    (
        "payment_requests.cancel",
        lambda client, value: client.payment_requests.cancel(value, "changed my mind"),
        "/v2/payment-requests/{}/cancel",
        "id",
        False,
    ),
    (
        "payment_requests.invoices.get",
        lambda client, value: client.payment_requests.invoices.get(value),
        "/v2/payment-requests/{}/invoices",
        "id",
        False,
    ),
    (
        "payment_requests.invoices.download id",
        lambda client, value: client.payment_requests.invoices.download("inv_1", value),
        "/v2/payment-requests/{}/invoices/inv_1/download",
        "id",
        False,
    ),
    (
        "payment_requests.invoices.download invoice_id",
        lambda client, value: client.payment_requests.invoices.download(value, "pl_1"),
        "/v2/payment-requests/pl_1/invoices/{}/download",
        "invoice_id",
        False,
    ),
    (
        "payouts.get",
        lambda client, value: client.payouts.get(value),
        "/v1/payouts/{}",
        "identifier",
        False,
    ),
    (
        "getPaymentLinkInformation",
        lambda client, value: client.getPaymentLinkInformation(value),
        "/v2/payment-requests/{}",
        "orderId",
        True,
    ),
    (
        "cancelPaymentLink",
        lambda client, value: client.cancelPaymentLink(value, "changed my mind"),
        "/v2/payment-requests/{}/cancel",
        "orderId",
        True,
    ),
]

ENCODED_VALUES = [
    ("pl_123abc", "pl_123abc"),
    (123456, "123456"),
    (2**53 - 1, str(2**53 - 1)),
    ("../x", "..%2Fx"),
    ("a/b", "a%2Fb"),
    ("a?b", "a%3Fb"),
    ("a#b", "a%23b"),
    ("a%2Fb", "a%252Fb"),
]

REJECTED_VALUES = [
    ("", "must be a non-empty string or a safe integer"),
    (".", "must not be a dot segment"),
    ("..", "must not be a dot segment"),
    (-1, "must be a non-negative safe integer"),
    (2**53, "must be a non-negative safe integer"),
]

CALL_SITE_IDS = [site[0] for site in CALL_SITES]


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


async def _call(call: Callable[[Any, Any], Any], client: Any, value: Any) -> Any:
    result = call(client, value)
    if inspect.isawaitable(result):
        result = await result
    return result


def _assert_rejected(
    excinfo: pytest.ExceptionInfo[Exception], name: str, legacy: bool, reason: str
):
    if legacy:
        assert excinfo.type is ValueError
        assert str(excinfo.value) == f"Invalid Parameter. {name} {reason}"
    else:
        assert excinfo.type is PayOSError
        assert str(excinfo.value) == f"{name} {reason}"


class TestPathSegments:
    """Identifiers are sent as one percent-encoded path segment by the sync client."""

    @pytest.mark.parametrize(("value", "encoded"), ENCODED_VALUES)
    @pytest.mark.parametrize("site", CALL_SITES, ids=CALL_SITE_IDS)
    def test_identifier_is_single_encoded_segment(
        self, httpx_mock: HTTPXMock, site: CallSite, value: Any, encoded: str
    ):
        """Test the outgoing path contains the identifier as exactly one encoded segment."""
        _, call, template, _, _ = site
        httpx_mock.add_response(status_code=404, json={"code": "101", "desc": "not found"})

        with pytest.raises((APIError, LegacyPayOSError)):
            call(_sync_client(), value)

        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.raw_path.decode("ascii") == template.format(encoded)

    @pytest.mark.parametrize(("value", "reason"), REJECTED_VALUES)
    @pytest.mark.parametrize("site", CALL_SITES, ids=CALL_SITE_IDS)
    def test_invalid_identifier_is_rejected_before_sending(
        self, httpx_mock: HTTPXMock, site: CallSite, value: Any, reason: str
    ):
        """Test empty, dot segment, negative and unsafe integer identifiers are rejected."""
        _, call, _, name, legacy = site

        with pytest.raises(Exception) as excinfo:
            call(_sync_client(), value)

        _assert_rejected(excinfo, name, legacy, reason)
        assert httpx_mock.get_requests() == []


class TestAsyncPathSegments:
    """Identifiers are sent as one percent-encoded path segment by the async client."""

    @pytest.mark.parametrize(("value", "encoded"), ENCODED_VALUES)
    @pytest.mark.parametrize("site", CALL_SITES, ids=CALL_SITE_IDS)
    async def test_identifier_is_single_encoded_segment(
        self, httpx_mock: HTTPXMock, site: CallSite, value: Any, encoded: str
    ):
        """Test the outgoing path contains the identifier as exactly one encoded segment."""
        _, call, template, _, _ = site
        httpx_mock.add_response(status_code=404, json={"code": "101", "desc": "not found"})

        with pytest.raises((APIError, LegacyPayOSError)):
            await _call(call, _async_client(), value)

        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.raw_path.decode("ascii") == template.format(encoded)

    @pytest.mark.parametrize(("value", "reason"), REJECTED_VALUES)
    @pytest.mark.parametrize("site", CALL_SITES, ids=CALL_SITE_IDS)
    async def test_invalid_identifier_is_rejected_before_sending(
        self, httpx_mock: HTTPXMock, site: CallSite, value: Any, reason: str
    ):
        """Test empty, dot segment, negative and unsafe integer identifiers are rejected."""
        _, call, _, name, legacy = site

        with pytest.raises(Exception) as excinfo:
            await _call(call, _async_client(), value)

        _assert_rejected(excinfo, name, legacy, reason)
        assert httpx_mock.get_requests() == []
