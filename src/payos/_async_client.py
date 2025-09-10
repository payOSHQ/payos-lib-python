"""Asynchronous payOS client."""

import asyncio
import email.utils
import json
import logging
import random
import time
from functools import cached_property
from types import TracebackType
from typing import Any, Optional, TypeVar, Union
from urllib.parse import urlencode, urljoin

from typing_extensions import Unpack

from ._core import (
    FileDownloadResponse,
    FinalRequestOptions,
)
from ._core.exceptions import (
    APIError,
    ConnectionError,
    ConnectionTimeoutError,
    InvalidSignatureError,
    PayOSError,
)
from ._core.request_options import RequestOptions
from ._crypto import CryptoProvider
from ._version import __version__
from .utils import (
    cast_to as cast_response_to,
    get_env_var,
    request_to_dict,
    response_to_dict,
    validate_positive_number,
)
from .utils.logs import SensitiveHeadersFilter

try:
    import httpx
except ImportError:
    raise ImportError("The payOS SDK requires httpx. Install it with: pip install httpx") from None

from .resources.v1.payouts import AsyncPayouts
from .resources.v1.payouts_account import AsyncPayoutsAccount
from .resources.v2.payment_requests import AsyncPaymentRequests
from .resources.webhooks import AsyncWebhooks

T = TypeVar("T")
ResponseT = TypeVar("ResponseT")
log: logging.Logger = logging.getLogger(__name__)
log.addFilter(SensitiveHeadersFilter())

DEFAULT_BASE_URL = "https://api-merchant.payos.vn"
DEFAULT_TIMEOUT = 60.0
DEFAULT_MAX_RETRIES = 2


class AsyncPayOS:
    """Asynchronous payOS API client."""

    client_id: str
    api_key: str
    checksum_key: str

    def __init__(
        self,
        client_id: Optional[str] = None,
        api_key: Optional[str] = None,
        checksum_key: Optional[str] = None,
        partner_code: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        """Initialize async payOS client.

        Args:
            client_id: payOS client ID. Defaults to PAYOS_CLIENT_ID env var.
            api_key: payOS API key. Defaults to PAYOS_API_KEY env var.
            checksum_key: payOS checksum key. Defaults to PAYOS_CHECKSUM_KEY env var.
            partner_code: Optional partner code. Defaults to PAYOS_PARTNER_CODE env var.
            base_url: API base URL. Defaults to PAYOS_BASE_URL env var or official URL.
            timeout: Request timeout in seconds. Defaults to 60.
            max_retries: Maximum number of retries. Defaults to 2.
            http_client: Custom httpx.AsyncClient instance.
        """
        # Required credentials
        if client_id is None:
            client_id = get_env_var("PAYOS_CLIENT_ID")
        if not client_id:
            raise PayOSError(
                "The PAYOS_CLIENT_ID environment variable is missing or empty; "
                "either provide it, or instantiate the payOS client with a client_id option."
            )
        self.client_id = client_id

        if api_key is None:
            api_key = get_env_var("PAYOS_API_KEY")
        if not api_key:
            raise PayOSError(
                "The PAYOS_API_KEY environment variable is missing or empty; "
                "either provide it, or instantiate the payOS client with an api_key option."
            )
        self.api_key = api_key

        if checksum_key is None:
            checksum_key = get_env_var("PAYOS_CHECKSUM_KEY")
        if not checksum_key:
            raise PayOSError(
                "The PAYOS_CHECKSUM_KEY environment variable is missing or empty; "
                "either provide it, or instantiate the payOS client with a checksum_key option."
            )
        self.checksum_key = checksum_key

        # Optional configuration
        self.partner_code = partner_code or get_env_var("PAYOS_PARTNER_CODE")
        self.base_url = base_url or get_env_var("PAYOS_BASE_URL") or DEFAULT_BASE_URL
        self.timeout = timeout if timeout is not None else DEFAULT_TIMEOUT
        self.max_retries = max_retries if max_retries is not None else DEFAULT_MAX_RETRIES

        # Validate timeout
        if self.timeout is not None:
            validate_positive_number("timeout", self.timeout)

        # Set up crypto provider
        self.crypto = CryptoProvider()

        # Set up HTTP client
        self._http_client = http_client or httpx.AsyncClient()
        self._own_http_client = http_client is None

    @property
    def user_agent(self) -> str:
        return f"{self.__class__.__name__}/Python {__version__}"

    async def aclose(self) -> None:
        """Close the HTTP client if we own it."""
        if self._own_http_client and self._http_client is not None:
            await self._http_client.aclose()

    async def __aenter__(self) -> "AsyncPayOS":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.aclose()

    def _build_headers(self, additional_headers: Optional[dict[str, str]] = None) -> dict[str, str]:
        """Build headers for API requests."""
        headers = {
            "x-client-id": self.client_id,
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": self.user_agent,
        }

        if self.partner_code:
            headers["x-partner-code"] = self.partner_code

        if additional_headers:
            headers.update(additional_headers)

        return headers

    def _build_url(
        self, path: str, query: Optional[dict[str, Any]] = None, url: Optional[str] = None
    ) -> str:
        """Build full URL from path and query parameters."""
        url = urljoin(self.base_url, path.lstrip("/"))

        if query:
            # Filter out None values and convert to strings
            filtered_query = {}
            for key, value in query.items():
                if value is not None:
                    if isinstance(value, (dict, list)):
                        filtered_query[key] = json.dumps(value)
                    else:
                        filtered_query[key] = str(value)

            if filtered_query:
                url += "?" + urlencode(filtered_query)

        return url

    def _build_body(self, body: Any) -> Optional[Union[str, bytes]]:
        """Build request body."""
        if body is None:
            return None

        if isinstance(body, (str, bytes)):
            return body

        try:
            from ._core.models import PayOSBaseModel

            if isinstance(body, PayOSBaseModel):
                if hasattr(body, "model_dump_camel_case"):
                    body = body.model_dump_camel_case()
                else:
                    body = body.model_dump(by_alias=True)
        except ImportError:
            pass

        if isinstance(body, dict):
            return json.dumps(body)

        try:
            return json.dumps(body)
        except TypeError:
            return str(body)

    def _build_request(self, options: FinalRequestOptions) -> httpx.Request:
        url = self._build_url(options.path or "", options.query, options.url)
        body = options.body
        if body is not None:
            body = self._handle_signature(options, body)
        headers = self._build_headers(options.headers)
        request_body = self._build_body(body)

        return self._http_client.build_request(
            url=url,
            method=options.method,
            headers=headers,
            content=request_body,
            timeout=self.timeout if not options.timeout else options.timeout,
        )

    def _should_retry(self, response: httpx.Response, retry_count: int) -> bool:
        """Determine if request should be retried."""
        if retry_count >= self.max_retries:
            return False

        if response.status_code in [408, 429] or response.status_code >= 500:
            return True

        return False

    def _calculate_retry_delay(self, retry_count: int, response_headers: httpx.Headers) -> float:
        """Calculate delay before retry."""

        # Check for Retry-After header
        # About the Retry-After header: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Retry-After
        timeout_ms: Union[float, None] = None
        retry_after = response_headers.get("retry-after")
        rate_limit_reset = response_headers.get("x-ratelimit-reset")
        if retry_after:
            try:
                timeout_ms = float(retry_after)
            except ValueError:
                pass

            retry_date_tuple = email.utils.parsedate_tz(retry_after)
            if retry_date_tuple is not None:
                retry_date = email.utils.mktime_tz(retry_date_tuple)
                timeout_ms = float(retry_date) - time.time()

        if rate_limit_reset:
            timeout_ms = float(rate_limit_reset) - time.time()

        if timeout_ms is not None and 0 < timeout_ms <= 60:
            return timeout_ms

        # Exponential backoff with jitter
        base_delay = 0.5
        max_delay = 10.0
        delay: float = min(base_delay * (2**retry_count), max_delay)

        # Add jitter (random factor between 0.75 and 1.0)

        jitter = 0.75 + random.random() * 0.25

        return delay * jitter

    def _handle_signature(self, options: FinalRequestOptions, body: Any) -> Any:
        """Handle request signature generation."""
        if not options.signature_request or not body:
            return body

        original_body = body
        try:
            from ._core.models import PayOSBaseModel

            if isinstance(body, PayOSBaseModel):
                if hasattr(body, "model_dump_camel_case"):
                    body_dict = body.model_dump_camel_case()
                else:
                    body_dict = body.model_dump(by_alias=True)
            elif isinstance(body, str):
                try:
                    body_dict = json.loads(body)
                except json.JSONDecodeError:
                    raise InvalidSignatureError(
                        "Invalid JSON body for signature generation"
                    ) from None
            else:
                body_dict = body
        except ImportError:
            if isinstance(body, str):
                try:
                    body_dict = json.loads(body)
                except json.JSONDecodeError:
                    raise InvalidSignatureError(
                        "Invalid JSON body for signature generation"
                    ) from None
            else:
                body_dict = body

        if not isinstance(body_dict, dict):
            raise InvalidSignatureError("Body must be a dictionary for signature generation")

        signature = None
        if options.signature_request == "create-payment-link":
            signature = self.crypto.create_signature_of_payment_request(
                body_dict,
                self.checksum_key,
            )
        elif options.signature_request == "body":
            signature = self.crypto.create_signature_from_object(body_dict, self.checksum_key)
        elif options.signature_request == "header":
            signature = self.crypto.create_signature(self.checksum_key, body_dict)

        if not signature:
            raise InvalidSignatureError("Failed to generate signature")

        if options.signature_request in ["create-payment-link", "body"]:
            body_dict["signature"] = signature
            return body_dict
        else:  # header
            options.headers = options.headers or {}
            options.headers["x-signature"] = signature
            return original_body

    def _verify_response_signature(
        self, options: FinalRequestOptions, response_data: Any, response_signature: Optional[str]
    ) -> None:
        """Verify response signature."""
        if not options.signature_response or not response_data:
            return

        if not response_signature:
            raise InvalidSignatureError("Response signature missing")

        if options.signature_response == "body":
            expected_signature = self.crypto.create_signature_from_object(
                response_data,
                self.checksum_key,
            )
        elif options.signature_response == "header":
            expected_signature = self.crypto.create_signature(self.checksum_key, response_data)
        else:
            raise InvalidSignatureError("Invalid signature response type")

        if not expected_signature or response_signature != expected_signature:
            raise InvalidSignatureError("Response signature verification failed")

    async def request(
        self,
        options: FinalRequestOptions,
        *,
        retry_count: int = 0,
        cast_to: type[ResponseT],
    ) -> ResponseT:
        """Make HTTP request with retry logic."""
        max_retries = options.max_retries if options.max_retries is not None else self.max_retries
        request = self._build_request(options=options)
        log.debug("Request options: %s", request_to_dict(request))

        try:
            response = await self._http_client.send(request=request)

            if not response.is_success:
                should_retry = self._should_retry(response, retry_count)

                error_data = None
                try:
                    error_json = response.json()
                    error_data = error_json
                except Exception:
                    pass

                if should_retry:
                    delay = self._calculate_retry_delay(retry_count, response.headers)
                    log.info("Retrying request to %s in %f seconds", request.url, delay)
                    await asyncio.sleep(delay)
                    return await self.request(
                        options,
                        cast_to=cast_to,
                        retry_count=retry_count + 1,
                    )

                raise APIError.from_response(response, error_data=error_data) from None

            log.debug("HTTP Response: %s", response_to_dict(response=response))

            try:
                response_json = response.json()
            except Exception:
                raise APIError(
                    f"Invalid JSON response: {response.text[:200]}",
                    status_code=response.status_code,
                    response=response,
                ) from None

            code = response_json.get("code")
            desc = response_json.get("desc")
            data = response_json.get("data")
            signature = response_json.get("signature")

            if code != "00":
                raise APIError(
                    desc or "API error",
                    error_code=code,
                    error_desc=desc,
                    status_code=response.status_code,
                    response=response,
                )

            if options.signature_response == "body":
                self._verify_response_signature(options, data, signature)
            elif options.signature_response == "header":
                header_signature = response.headers.get("x-signature")
                self._verify_response_signature(options, data, header_signature)

            return cast_response_to(cast_to, data)

        except httpx.TimeoutException:
            log.debug("Encountered httpx.TimeoutException", exc_info=True)
            if retry_count < max_retries:
                delay = self._calculate_retry_delay(retry_count, httpx.Headers())
                log.info("Retrying request to %s in %f seconds", request.url, delay)
                await asyncio.sleep(delay)
                return await self.request(
                    options,
                    cast_to=cast_to,
                    retry_count=retry_count + 1,
                )
            raise ConnectionTimeoutError("Request timed out") from None

        except httpx.ConnectError:
            log.debug("Encountered Exception", exc_info=True)
            if retry_count < max_retries:
                delay = self._calculate_retry_delay(retry_count, httpx.Headers())
                log.info("Retrying request to %s in %f seconds", request.url, delay)
                await asyncio.sleep(delay)
                return await self.request(
                    options,
                    cast_to=cast_to,
                    retry_count=retry_count + 1,
                )
            raise ConnectionError("Failed to connect") from None

        except Exception:
            raise

    async def get(
        self, path: str, *, cast_to: type[ResponseT], **kwargs: Unpack[RequestOptions]
    ) -> ResponseT:
        """Make GET request."""
        options = FinalRequestOptions(method="GET", path=path, **kwargs)
        return await self.request(options, cast_to=cast_to)

    async def post(
        self, path: str, *, cast_to: type[ResponseT], **kwargs: Unpack[RequestOptions]
    ) -> ResponseT:
        """Make POST request."""
        options = FinalRequestOptions(method="POST", path=path, **kwargs)
        return await self.request(options, cast_to=cast_to)

    async def put(
        self, path: str, *, cast_to: type[ResponseT], **kwargs: Unpack[RequestOptions]
    ) -> ResponseT:
        """Make PUT request."""
        options = FinalRequestOptions(method="PUT", path=path, **kwargs)
        return await self.request(options, cast_to=cast_to)

    async def patch(
        self, path: str, *, cast_to: type[ResponseT], **kwargs: Unpack[RequestOptions]
    ) -> ResponseT:
        """Make PATCH request."""
        options = FinalRequestOptions(method="PATCH", path=path, **kwargs)
        return await self.request(options, cast_to=cast_to)

    async def delete(
        self, path: str, *, cast_to: type[ResponseT], **kwargs: Unpack[RequestOptions]
    ) -> ResponseT:
        """Make DELETE request."""
        options = FinalRequestOptions(method="DELETE", path=path, **kwargs)
        return await self.request(options, cast_to=cast_to)

    async def download(self, path: str, **kwargs: Unpack[RequestOptions]) -> FileDownloadResponse:
        """Download a file from the API."""
        from ._core import FileDownloadResponse

        options = FinalRequestOptions(method="GET", path=path, **kwargs)
        request = self._build_request(options)

        try:
            response = await self._http_client.send(request=request)
            if not response.is_success:
                error_data = None
                try:
                    error_json = response.json()
                    error_data = error_json
                except Exception:
                    pass
                raise APIError.from_response(response, error_data=error_data)

            filename = None
            content_disposition = response.headers.get("content-disposition")
            if content_disposition:
                import re

                match = re.search(r'filename="([^"]+)"', content_disposition)
                if match:
                    filename = match.group(1)

            if not filename:
                from urllib.parse import urlparse

                parsed_url = urlparse(str(request.url))
                filename = parsed_url.path.split("/")[-1] if parsed_url.path else None

            content_size = len(response.content)
            return FileDownloadResponse(
                data=response.content,
                filename=filename,
                content_type=response.headers.get("content-type"),
                size=content_size,
                headers=dict(response.headers),
            )

        except httpx.TimeoutException:
            raise ConnectionTimeoutError("Download request timed out") from None

        except httpx.ConnectError:
            raise ConnectionError("Failed to connect for download") from None

        except Exception:
            raise

    @cached_property
    def payment_requests(self) -> AsyncPaymentRequests:
        return AsyncPaymentRequests(self)

    @cached_property
    def webhooks(self) -> AsyncWebhooks:
        return AsyncWebhooks(self)

    @cached_property
    def payouts(self) -> AsyncPayouts:
        return AsyncPayouts(self)

    @cached_property
    def payouts_account(self) -> AsyncPayoutsAccount:
        return AsyncPayoutsAccount(self)
