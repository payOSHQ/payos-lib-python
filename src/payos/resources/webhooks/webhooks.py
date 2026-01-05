"""payOS webhooks resource."""

from typing import Any, Union

from pydantic import ValidationError

from ..._core.exceptions import PayOSError, WebhookError
from ...types.webhooks import (
    ConfirmWebhookRequest,
    ConfirmWebhookResponse,
    Webhook,
    WebhookData,
)
from ...utils.json_utils import safe_json_parse
from .._base import AsyncBaseResource, BaseResource


class Webhooks(BaseResource):
    """Synchronous Webhooks resource."""

    def confirm(self, webhook_url: str, **kwargs: Any) -> ConfirmWebhookResponse:
        """
        Validate and register a webhook URL with payOS.
        payOS will test the webhook endpoint by sending a validation request to it.
        If the webhook responds correctly, it will be registered for payment notifications.
        """
        if not webhook_url or len(webhook_url.strip()) == 0:
            raise WebhookError("Webhook URL invalid.")

        try:
            response = self._client.post(
                "/confirm-webhook",
                body=ConfirmWebhookRequest(webhook_url=webhook_url),
                cast_to=ConfirmWebhookResponse,
                **kwargs,
            )
            return response
        except PayOSError as error:
            # Re-throw with more descriptive messages based on payOS validation response
            raise WebhookError(f"Webhook validation failed: {error}") from error
        except Exception as error:
            raise error

    def verify(self, payload: Union[str, bytes, dict, Webhook]) -> WebhookData:
        """
        Verify the webhook data sent from payOS.
        """
        if isinstance(payload, Webhook):
            webhook = payload
        else:
            if isinstance(payload, (bytes, bytearray)):
                payload_str = payload.decode("utf-8")
                payload_obj = safe_json_parse(payload_str)
                if not payload_obj:
                    raise WebhookError("Invalid JSON")
            elif isinstance(payload, str):
                payload_obj = safe_json_parse(payload)
                if not payload_obj:
                    raise WebhookError("Invalid JSON")
            elif isinstance(payload, dict):
                payload_obj = payload
            else:
                raise WebhookError(f"Unsupported payload type: {type(payload)}")
            try:
                webhook = Webhook(**payload_obj)
            except ValidationError as e:
                raise WebhookError(f"Webhook schema validation failed: {e}") from e

        data = webhook.data
        signature = webhook.signature

        if not data:
            raise WebhookError("Invalid webhook data")

        if not signature:
            raise WebhookError("Invalid signature")

        if not self._client.checksum_key:
            raise WebhookError("Checksum key not configured")

        # Cast to Dict for signature verification
        data_dict = dict(data.model_dump_camel_case())
        signed_signature = self._client.crypto.create_signature_from_object(
            data_dict, self._client.checksum_key
        )

        if not signed_signature or signed_signature != signature:
            raise WebhookError("Data not integrity")

        return data


class AsyncWebhooks(AsyncBaseResource):
    """Asynchronous Webhooks resource."""

    async def confirm(self, webhook_url: str, **kwargs: Any) -> ConfirmWebhookResponse:
        """
        Validate and register a webhook URL with payOS.
        payOS will test the webhook endpoint by sending a validation request to it.
        If the webhook responds correctly, it will be registered for payment notifications.
        """
        if not webhook_url or len(webhook_url.strip()) == 0:
            raise WebhookError("Webhook URL invalid.")

        try:
            response = await self._client.post(
                "/confirm-webhook",
                body=ConfirmWebhookRequest(webhook_url=webhook_url),
                cast_to=ConfirmWebhookResponse,
                **kwargs,
            )
            return response
        except PayOSError as error:
            # Re-throw with more descriptive messages based on payOS validation response
            raise WebhookError(f"Webhook validation failed: {error}") from error
        except Exception as error:
            raise error

    async def verify(self, payload: Union[str, bytes, dict, Webhook]) -> WebhookData:
        """
        Verify the webhook data sent from payOS.
        """
        if isinstance(payload, Webhook):
            webhook = payload
        else:
            if isinstance(payload, (bytes, bytearray)):
                payload_str = payload.decode("utf-8")
                payload_obj = safe_json_parse(payload_str)
                if not payload_obj:
                    raise WebhookError("Invalid JSON")
            elif isinstance(payload, str):
                payload_obj = safe_json_parse(payload)
                if not payload_obj:
                    raise WebhookError("Invalid JSON")
            elif isinstance(payload, dict):
                payload_obj = payload
            else:
                raise WebhookError(f"Unsupported payload type: {type(payload)}")
            try:
                webhook = Webhook(**payload_obj)
            except ValidationError as e:
                raise WebhookError(f"Webhook schema validation failed: {e}") from e

        data = webhook.data
        signature = webhook.signature

        if not data:
            raise WebhookError("Invalid webhook data")

        if not signature:
            raise WebhookError("Invalid signature")

        if not self._client.checksum_key:
            raise WebhookError("Checksum key not configured")

        # Cast to Dict for signature verification
        data_dict = dict(data.model_dump_camel_case())
        signed_signature = self._client.crypto.create_signature_from_object(
            data_dict, self._client.checksum_key
        )

        if not signed_signature or signed_signature != signature:
            raise WebhookError("Data not integrity")

        return data
