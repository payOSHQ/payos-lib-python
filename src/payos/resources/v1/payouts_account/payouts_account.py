"""payOS payouts account resource for API v1."""

from typing import Any, Optional

from ....types.v1 import PayoutAccountInfo
from ..._base import AsyncBaseResource, BaseResource


class PayoutsAccount(BaseResource):
    """Synchronous Payouts Account resource."""

    def balance(
        self,
        *,
        extra_headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> PayoutAccountInfo:
        """
        Retrieve the current payout account balance.
        """
        response = self._client.get(
            "/v1/payouts-account/balance",
            headers=extra_headers,
            cast_to=PayoutAccountInfo,
            signature_response="header",
            **kwargs,
        )
        return response


class AsyncPayoutsAccount(AsyncBaseResource):
    """Asynchronous Payouts Account resource."""

    async def balance(
        self,
        *,
        extra_headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> PayoutAccountInfo:
        """
        Retrieve the current payout account balance.
        """
        response = await self._client.get(
            "/v1/payouts-account/balance",
            headers=extra_headers,
            cast_to=PayoutAccountInfo,
            signature_response="header",
            **kwargs,
        )
        return response
