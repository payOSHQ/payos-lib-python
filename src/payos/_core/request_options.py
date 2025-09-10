"""Core request options and types."""

from typing import Any, Literal, Optional, TypedDict, TypeVar

import httpx
from typing_extensions import Unpack

ResponseT = TypeVar("ResponseT")

HTTPMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
HeadersType = dict[str, str]

SignatureRequestType = Literal["create-payment-link", "body", "header"]
SignatureResponseType = Literal["body", "header"]


class RequestOptions(TypedDict, total=False):
    url: Optional[str]
    query: Optional[dict[str, Any]]
    headers: Optional[HeadersType]
    body: Optional[Any]
    timeout: Optional[float]
    max_retries: Optional[int]
    signature_request: Optional[SignatureRequestType]
    signature_response: Optional[SignatureResponseType]


class FinalRequestOptions:
    """Options for making HTTP requests."""

    def __init__(
        self,
        *,
        method: HTTPMethod = "GET",
        path: Optional[str] = None,
        **opts: Unpack[RequestOptions],
    ) -> None:
        self.method = method
        self.path = path
        self.url = opts.get("url")
        self.query = opts.get("query")
        self.headers = opts.get("headers")
        self.body = opts.get("body")
        self.timeout = opts.get("timeout")
        self.max_retries = opts.get("max_retries")
        self.signature_request = opts.get("signature_request")
        self.signature_response = opts.get("signature_response")


class APIResponse:
    """Wrapper for API responses."""

    def __init__(
        self,
        *,
        data: Any = None,
        code: Optional[str] = None,
        desc: Optional[str] = None,
        signature: Optional[str] = None,
        raw_response: Optional[httpx.Response] = None,
    ) -> None:
        self.data = data
        self.code = code
        self.desc = desc
        self.signature = signature
        self.raw_response = raw_response

    @property
    def success(self) -> bool:
        """Check if the response indicates success."""
        return self.code == "00"


class FileDownloadResponse:
    """Response for file downloads."""

    def __init__(
        self,
        *,
        data: bytes,
        filename: Optional[str] = None,
        content_type: Optional[str] = None,
        size: Optional[int] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> None:
        self.data = data
        self.filename = filename
        self.content_type = content_type
        self.size = size or len(data)
        self.headers = headers or {}

    def save_to_file(self, filepath: str) -> None:
        """Save the downloaded content to a file."""
        import os

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "wb") as f:
            f.write(self.data)

    def save_to_directory(self, directory: str) -> str:
        """Save the downloaded content to a directory using the original filename."""
        import os

        if not self.filename:
            raise ValueError("No filename available for download")

        filepath = os.path.join(directory, self.filename)
        self.save_to_file(filepath)
        return filepath

    @property
    def text(self) -> str:
        """Get the content as text (for text files)."""
        return self.data.decode("utf-8")

    def __len__(self) -> int:
        """Return the size of the downloaded content."""
        return self.size

    def __repr__(self) -> str:
        return f"FileDownloadResponse(filename={self.filename!r}, size={self.size}, content_type={self.content_type!r})"
