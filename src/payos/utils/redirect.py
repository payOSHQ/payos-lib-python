"""Redirect handling that keeps the merchant credentials on the API origin."""

from typing import Optional

import httpx

MAX_REDIRECTS = 5
# httpx only drops ``Authorization`` on a cross-origin redirect, so ``x-api-key``/``x-client-id``/``x-partner-code``
# would be forwarded to whatever host the redirect points to.
_SENSITIVE_REDIRECT_HEADERS = (
    "x-api-key",
    "x-client-id",
    "x-partner-code",
    "authorization",
    "cookie",
    "proxy-authorization",
)
_DEFAULT_PORTS = {"http": 80, "https": 443}


def _origin(url: httpx.URL) -> tuple[str, str, Optional[int]]:
    return url.scheme, url.host, url.port or _DEFAULT_PORTS.get(url.scheme)


def build_redirect_request(
    request: httpx.Request, response: httpx.Response
) -> Optional[httpx.Request]:
    """Return the request that follows the redirect ``response``, or ``None`` when it is not a redirect.

    Credentials (``x-api-key``, ``x-client-id``, ``x-partner-code``, ``authorization``, ``cookie``,
    ``proxy-authorization``) are dropped when the redirect leaves the origin (scheme, host, port) of
    ``request``. A ``303``, or a ``301``/``302`` answering a ``POST``, switches to ``GET`` without body
    and ``Content-Type``.
    """
    location = response.headers.get("location")
    if not (300 <= response.status_code < 400) or not location:
        return None

    url = request.url.join(location)
    method = request.method
    switch_to_get = response.status_code == 303 or (
        response.status_code in (301, 302) and method == "POST"
    )

    headers = httpx.Headers(request.headers)
    # Recomputed by httpx for the new URL and body.
    for name in ("host", "content-length", "transfer-encoding"):
        headers.pop(name, None)
    if _origin(url) != _origin(request.url):
        for name in _SENSITIVE_REDIRECT_HEADERS:
            headers.pop(name, None)
    if switch_to_get:
        headers.pop("content-type", None)

    return httpx.Request(
        method="GET" if switch_to_get else method,
        url=url,
        headers=headers,
        content=None if switch_to_get else request.content,
        extensions=request.extensions,
    )
