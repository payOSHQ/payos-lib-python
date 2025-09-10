"""Invoices resource for payOS API v2."""

from typing import Any, Optional, Union

from ....._core.request_options import FileDownloadResponse
from .....types.v2 import (
    InvoicesInfo,
)
from ...._base import AsyncBaseResource, BaseResource


class Invoices(BaseResource):
    """Synchronous invoices resource."""

    def get(
        self,
        id: Union[str, int],
        *,
        extra_headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> InvoicesInfo:
        """
        Retrieve invoices of a payment link.
        """
        response = self._client.get(
            f"/v2/payment-requests/{id}/invoices",
            headers=extra_headers,
            cast_to=InvoicesInfo,
            signature_response="body",
            **kwargs,
        )
        return response

    def download(
        self,
        invoice_id: str,
        id: Union[str, int],
        *,
        extra_headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> FileDownloadResponse:
        """
        Download an invoice in PDF format.
        """
        response = self._client.download(
            f"/v2/payment-requests/{id}/invoices/{invoice_id}/download",
            headers=extra_headers,
            **kwargs,
        )
        return response


class AsyncInvoices(AsyncBaseResource):
    """Asynchronous invoices resource."""

    async def get(
        self,
        id: Union[str, int],
        *,
        extra_headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> InvoicesInfo:
        """
        Retrieve invoices of a payment link.
        """
        response = await self._client.get(
            f"/v2/payment-requests/{id}/invoices",
            headers=extra_headers,
            cast_to=InvoicesInfo,
            signature_response="body",
            **kwargs,
        )
        return response

    async def download(
        self,
        invoice_id: str,
        id: Union[str, int],
        *,
        extra_headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> FileDownloadResponse:
        """
        Download an invoice in PDF format.
        """
        response = await self._client.download(
            f"/v2/payment-requests/{id}/invoices/{invoice_id}/download",
            headers=extra_headers,
            **kwargs,
        )
        return response
