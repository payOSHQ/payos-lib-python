"""Payouts resource for payOS API v1."""

from functools import cached_property
from typing import Any, Optional, Union

from ...._core import AsyncPage, Page
from ...._core.request_options import FinalRequestOptions
from ....types.v1 import (
    EstimateCredit,
    GetPayoutListParams,
    Payout,
    PayoutBatchRequest,
    PayoutRequest,
)
from ....types.v1.payouts.payouts import PayoutListResponse
from ..._base import AsyncBaseResource, BaseResource
from .batch.batch import AsyncBatch, Batch


class Payouts(BaseResource):
    """Synchronous payouts resource."""

    def create(
        self,
        payout_data: PayoutRequest,
        *,
        idempotency_key: Optional[str] = None,
        extra_headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> Payout:
        """Create a new payout."""
        if idempotency_key is None:
            idempotency_key = self._client.crypto.create_uuid4()

        headers_with_idempotency = {
            "x-idempotency-key": idempotency_key,
            **(extra_headers or {}),
        }
        response = self._client.post(
            "/v1/payouts",
            body=payout_data,
            headers=headers_with_idempotency,
            cast_to=Payout,
            signature_request="header",
            signature_response="header",
            **kwargs,
        )
        return response

    def get(
        self,
        identifier: Union[str, int],
        *,
        extra_headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> Payout:
        """Retrieve details of a specific payout."""
        response = self._client.get(
            f"/v1/payouts/{identifier}",
            headers=extra_headers,
            cast_to=Payout,
            signature_response="header",
            **kwargs,
        )
        return response

    def list(
        self,
        params: Optional[GetPayoutListParams] = None,
        *,
        extra_headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> Page[Payout]:
        """List payouts with optional filtering."""
        response = self._client.get(
            "/v1/payouts",
            query=dict(params.model_dump_camel_case()) if params else None,
            headers=extra_headers,
            cast_to=PayoutListResponse,
            signature_response="header",
            **kwargs,
        )
        request_options = FinalRequestOptions(
            method="GET",
            path="/v1/payouts",
            query=dict(params.model_dump_camel_case()) if params else None,
            headers=extra_headers,
            signature_response="header",
            **kwargs,
        )
        return Page(
            self._client, PayoutListResponse, response.payouts, response.pagination, request_options
        )

    def estimate_credit(
        self,
        payout_data: Union[PayoutRequest, PayoutBatchRequest],
        *,
        extra_headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> EstimateCredit:
        """Estimate credit required for one or multiple payouts."""
        response = self._client.post(
            "/v1/payouts/estimate-credit",
            body=payout_data,
            headers=extra_headers,
            cast_to=EstimateCredit,
            signature_request="header",
            **kwargs,
        )
        return response

    @cached_property
    def batch(self) -> Batch:
        return Batch(self._client)


class AsyncPayouts(AsyncBaseResource):
    """Asynchronous payouts resource."""

    async def create(
        self,
        payout_data: PayoutRequest,
        *,
        idempotency_key: Optional[str] = None,
        extra_headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> Payout:
        """Create a new payout."""
        if idempotency_key is None:
            idempotency_key = self._client.crypto.create_uuid4()

        headers_with_idempotency = {
            "x-idempotency-key": idempotency_key,
            **(extra_headers or {}),
        }
        response = await self._client.post(
            "/v1/payouts",
            body=payout_data,
            headers=headers_with_idempotency,
            cast_to=Payout,
            signature_request="header",
            signature_response="header",
            **kwargs,
        )
        return response

    async def get(
        self,
        identifier: Union[str, int],
        *,
        extra_headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> Payout:
        """Retrieve details of a specific payout."""
        response = await self._client.get(
            f"/v1/payouts/{identifier}",
            headers=extra_headers,
            cast_to=Payout,
            signature_response="header",
            **kwargs,
        )
        return response

    async def list(
        self,
        params: Optional[GetPayoutListParams] = None,
        *,
        extra_headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> AsyncPage[Payout]:
        """List payouts with optional filtering."""
        response = await self._client.get(
            "/v1/payouts",
            query=dict(params.model_dump_camel_case()) if params else None,
            headers=extra_headers,
            cast_to=PayoutListResponse,
            **kwargs,
        )
        request_options = FinalRequestOptions(
            method="GET",
            path="/v1/payouts",
            query=dict(params.model_dump_camel_case()) if params else None,
            headers=extra_headers,
            signature_response="header",
            **kwargs,
        )
        return AsyncPage(
            self._client, PayoutListResponse, response.payouts, response.pagination, request_options
        )

    async def estimate_credit(
        self,
        payout_data: Union[PayoutRequest, PayoutBatchRequest],
        *,
        extra_headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> EstimateCredit:
        """Estimate credit required for one or multiple payouts."""
        response = await self._client.post(
            "/v1/payouts/estimate-credit",
            body=payout_data,
            headers=extra_headers,
            signature_request="header",
            cast_to=EstimateCredit,
            **kwargs,
        )
        return response

    @cached_property
    def batch(self) -> AsyncBatch:
        return AsyncBatch(self._client)
