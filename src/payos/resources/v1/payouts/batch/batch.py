"""Batch payout resource for payOS API v1."""

from typing import Any, Optional

from .....types.v1 import Payout, PayoutBatchRequest
from ...._base import AsyncBaseResource, BaseResource


class Batch(BaseResource):
    """Synchronous batch payout resource."""

    def create(
        self,
        batch_data: PayoutBatchRequest,
        *,
        idempotency_key: Optional[str] = None,
        extra_headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> Payout:
        """
        Create a batch payout.
        """
        if idempotency_key is None:
            idempotency_key = self._client.crypto.create_uuid4()

        headers_with_idempotency = {
            "x-idempotency-key": idempotency_key,
            **(extra_headers or {}),
        }

        response = self._client.post(
            "/v1/payouts/batch",
            body=batch_data,
            headers=headers_with_idempotency,
            signature_request="header",
            signature_response="header",
            cast_to=Payout,
            **kwargs,
        )
        return response


class AsyncBatch(AsyncBaseResource):
    """Asynchronous batch payout resource."""

    async def create(
        self,
        batch_data: PayoutBatchRequest,
        *,
        idempotency_key: Optional[str] = None,
        extra_headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> Payout:
        """
        Create a batch payout.
        """
        if idempotency_key is None:
            idempotency_key = self._client.crypto.create_uuid4()

        headers_with_idempotency = {
            "x-idempotency-key": idempotency_key,
            **(extra_headers or {}),
        }

        response = await self._client.post(
            "/v1/payouts/batch",
            body=batch_data,
            headers=headers_with_idempotency,
            cast_to=Payout,
            signature_request="header",
            signature_response="header",
            **kwargs,
        )
        return response
