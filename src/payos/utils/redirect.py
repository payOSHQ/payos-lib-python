"""Redirect handling that keeps the merchant credentials on the API origin."""

from collections.abc import Generator
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
_REDIRECT_STATUSES = (301, 302, 303, 307, 308)
_DEFAULT_PORTS = {"http": 80, "https": 443}


def _origin(url: httpx.URL) -> tuple[str, str, Optional[int]]:
    return url.scheme, url.host, url.port or _DEFAULT_PORTS.get(url.scheme)


class NoAuth(httpx.Auth):
    """Sends the request as built; stops httpx from re-applying client auth or URL userinfo on a redirect."""

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        yield request


def build_redirect_request(
    response: httpx.Response,
    *,
    original_url: httpx.URL,
    left_origin: bool,
    cookies: httpx.Cookies,
) -> Optional[tuple[httpx.Request, bool]]:
    """Return the request that follows the redirect ``response`` and the updated ``left_origin`` flag.

    Returns ``None`` when ``response`` is not a 301/302/303/307/308 with a ``Location`` header. Once the chain
    leaves the origin (scheme, host, port) of ``original_url``, ``left_origin`` stays ``True`` and the
    credential headers (``x-api-key``, ``x-client-id``, ``x-partner-code``, ``authorization``, ``cookie``,
    ``proxy-authorization``) are never sent again. Before that, the ``Cookie`` header is rebuilt from
    ``cookies``. A ``303``, or a ``301``/``302`` answering a ``POST``, switches to ``GET`` without body and
    ``Content-Type``.
    """
    location = response.headers.get("location")
    if response.status_code not in _REDIRECT_STATUSES or not location:
        return None

    request = response.request
    url = request.url.join(location).copy_with(userinfo=b"")
    method = request.method
    switch_to_get = response.status_code == 303 or (
        response.status_code in (301, 302) and method == "POST"
    )

    headers = httpx.Headers(request.headers)
    # Recomputed by httpx for the new URL and body; the cookie header is rebuilt below.
    for name in ("host", "content-length", "transfer-encoding", "cookie"):
        headers.pop(name, None)
    left_origin = left_origin or _origin(url) != _origin(original_url)
    if left_origin:
        for name in _SENSITIVE_REDIRECT_HEADERS:
            headers.pop(name, None)
    if switch_to_get:
        headers.pop("content-type", None)

    next_request = httpx.Request(
        method="GET" if switch_to_get else method,
        url=url,
        headers=headers,
        content=None if switch_to_get else request.content,
        extensions=request.extensions,
    )
    if not left_origin:
        cookies.set_cookie_header(next_request)
    return next_request, left_origin
