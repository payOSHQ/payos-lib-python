"""Payment requests resource for payOS API v2."""

from functools import cached_property
from typing import Any, Optional, Union

from ....types.v2 import (
    CancelPaymentLinkRequest,
    CreatePaymentLinkRequest,
    CreatePaymentLinkResponse,
    PaymentLink,
)
from ..._base import AsyncBaseResource, BaseResource
from .invoices import AsyncInvoices, Invoices


class PaymentRequests(BaseResource):
    """Synchronous payment requests resource."""

    def create(
        self,
        payment_data: CreatePaymentLinkRequest,
        *,
        extra_headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> CreatePaymentLinkResponse:
        """Create a payment link."""
        response = self._client.post(
            "/v2/payment-requests",
            body=payment_data,
            headers=extra_headers,
            cast_to=CreatePaymentLinkResponse,
            signature_request="create-payment-link",
            signature_response="body",
            **kwargs,
        )
        return response

    def get(
        self,
        id: Union[str, int],
        *,
        extra_headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> PaymentLink:
        """Get payment link information."""
        response = self._client.get(
            f"/v2/payment-requests/{id}",
            headers=extra_headers,
            cast_to=PaymentLink,
            signature_response="body",
            **kwargs,
        )
        return response

    def cancel(
        self,
        id: Union[str, int],
        cancellation_reason: Optional[str] = None,
        *,
        extra_headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> PaymentLink:
        """Cancel a payment link."""
        response = self._client.post(
            f"/v2/payment-requests/{id}/cancel",
            body=(
                CancelPaymentLinkRequest(cancellation_reason=cancellation_reason)
                if cancellation_reason
                else {}
            ),
            headers=extra_headers,
            cast_to=PaymentLink,
            signature_request="body",
            signature_response="body",
            **kwargs,
        )
        return response

    @cached_property
    def invoices(self) -> Invoices:
        return Invoices(self._client)


class AsyncPaymentRequests(AsyncBaseResource):
    """Asynchronous payment requests resource."""

    async def create(
        self,
        payment_data: CreatePaymentLinkRequest,
        *,
        extra_headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> CreatePaymentLinkResponse:
        """Create a payment link."""
        response = await self._client.post(
            "/v2/payment-requests",
            body=payment_data,
            headers=extra_headers,
            cast_to=CreatePaymentLinkResponse,
            signature_request="create-payment-link",
            signature_response="body",
            **kwargs,
        )
        return response

    async def get(
        self,
        id: Union[str, int],
        *,
        extra_headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> PaymentLink:
        """Get payment link information."""
        response = await self._client.get(
            f"/v2/payment-requests/{id}",
            headers=extra_headers,
            cast_to=PaymentLink,
            signature_response="body",
            **kwargs,
        )
        return response

    async def cancel(
        self,
        id: Union[str, int],
        cancellation_reason: Optional[str] = None,
        *,
        extra_headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> PaymentLink:
        """Cancel a payment link."""
        response = await self._client.post(
            f"/v2/payment-requests/{id}/cancel",
            body=(
                CancelPaymentLinkRequest(cancellation_reason=cancellation_reason)
                if cancellation_reason
                else {}
            ),
            headers=extra_headers,
            cast_to=PaymentLink,
            signature_request="body",
            signature_response="body",
            **kwargs,
        )
        return response

    @cached_property
    def invoices(self) -> AsyncInvoices:
        return AsyncInvoices(self._client)
