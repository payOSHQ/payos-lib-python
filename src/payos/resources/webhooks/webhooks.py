"""payOS webhooks resource."""

from typing import Any, Union

from ..._core.exceptions import PayOSError, WebhookError
from ..._crypto import constant_time_equal
from ...types.webhooks import (
    ConfirmWebhookRequest,
    ConfirmWebhookResponse,
    Webhook,
    WebhookData,
)
from .._base import AsyncBaseResource, BaseResource
from ._validation import (
    load_json_no_duplicates,
    validate_model_values,
    validate_webhook_data,
)


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
            data = webhook.data
            signature = webhook.signature

            if not data:
                raise WebhookError("Invalid webhook data")

            if not signature:
                raise WebhookError("Invalid signature")

            if not self._client.checksum_key:
                raise WebhookError("Checksum key not configured")

            data_dict = dict(data.model_dump_camel_case())
            validate_model_values(data_dict)
            signed_signature = self._client.crypto.create_signature_from_object(
                data_dict, self._client.checksum_key
            )

            if not signed_signature or not constant_time_equal(signed_signature, signature):
                raise WebhookError("Data not integrity")

            return webhook.data

        payload_obj: object
        if isinstance(payload, (bytes, bytearray)):
            try:
                payload_str = payload.decode("utf-8")
            except UnicodeDecodeError as e:
                raise WebhookError("Invalid JSON") from e
            payload_obj = load_json_no_duplicates(payload_str)
        elif isinstance(payload, str):
            payload_obj = load_json_no_duplicates(payload)
        elif isinstance(payload, dict):
            payload_obj = payload
        else:
            raise WebhookError(f"Unsupported payload type: {type(payload)}")

        if not isinstance(payload_obj, dict):
            raise WebhookError("Invalid webhook data")

        wire_data = payload_obj.get("data")
        if wire_data is None:
            raise WebhookError("Invalid webhook data")
        validate_webhook_data(wire_data)

        wire_signature = payload_obj.get("signature")
        if not isinstance(wire_signature, str) or not wire_signature:
            raise WebhookError("Invalid signature")

        if not self._client.checksum_key:
            raise WebhookError("Checksum key not configured")

        signed = self._client.crypto.create_signature_from_object(
            wire_data, self._client.checksum_key
        )
        if not signed or not constant_time_equal(signed, wire_signature):
            raise WebhookError("Data not integrity")

        return WebhookData.model_validate(wire_data)


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
            data = webhook.data
            signature = webhook.signature

            if not data:
                raise WebhookError("Invalid webhook data")

            if not signature:
                raise WebhookError("Invalid signature")

            if not self._client.checksum_key:
                raise WebhookError("Checksum key not configured")

            data_dict = dict(data.model_dump_camel_case())
            validate_model_values(data_dict)
            signed_signature = self._client.crypto.create_signature_from_object(
                data_dict, self._client.checksum_key
            )

            if not signed_signature or not constant_time_equal(signed_signature, signature):
                raise WebhookError("Data not integrity")

            return webhook.data

        payload_obj: object
        if isinstance(payload, (bytes, bytearray)):
            try:
                payload_str = payload.decode("utf-8")
            except UnicodeDecodeError as e:
                raise WebhookError("Invalid JSON") from e
            payload_obj = load_json_no_duplicates(payload_str)
        elif isinstance(payload, str):
            payload_obj = load_json_no_duplicates(payload)
        elif isinstance(payload, dict):
            payload_obj = payload
        else:
            raise WebhookError(f"Unsupported payload type: {type(payload)}")

        if not isinstance(payload_obj, dict):
            raise WebhookError("Invalid webhook data")

        wire_data = payload_obj.get("data")
        if wire_data is None:
            raise WebhookError("Invalid webhook data")
        validate_webhook_data(wire_data)

        wire_signature = payload_obj.get("signature")
        if not isinstance(wire_signature, str) or not wire_signature:
            raise WebhookError("Invalid signature")

        if not self._client.checksum_key:
            raise WebhookError("Checksum key not configured")

        signed = self._client.crypto.create_signature_from_object(
            wire_data, self._client.checksum_key
        )
        if not signed or not constant_time_equal(signed, wire_signature):
            raise WebhookError("Data not integrity")

        return WebhookData.model_validate(wire_data)
