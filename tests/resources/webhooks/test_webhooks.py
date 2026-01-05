"""Tests for webhooks resource."""

import pytest
from pytest_httpx import HTTPXMock

from payos import AsyncPayOS, PayOS, WebhookError
from payos.types.webhooks import ConfirmWebhookResponse, Webhook, WebhookData

# Constants
CLIENT_ID = "test-client-id"
API_KEY = "test-api-key"
CHECKSUM_KEY = "test-checksum-key"
BASE_URL = "https://api-test.payos.vn"


class TestWebhooks:
    """Synchronous tests for Webhooks."""

    def test_verify_valid_webhook(self, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch):
        """Test verifying valid webhook with correct signature."""
        valid_webhook_data = WebhookData(
            account_number="0123456789",
            amount=20000,
            description="thanh toan",
            reference="FT-REFERENCE",
            transaction_date_time="2025-12-12 09:00:00",
            virtual_account_number="",
            counter_account_bank_id="01202001",
            counter_account_bank_name="",
            counter_account_name="NGUYEN VAN A",
            counter_account_number="9876543210",
            virtual_account_name="",
            currency="VND",
            order_code=0,
            payment_link_id="payment-link-id",
            code="00",
            desc="success",
        )

        valid_signature = "mock-valid-signature"
        webhook = Webhook(
            code="00",
            desc="success",
            success=True,
            data=valid_webhook_data,
            signature=valid_signature,
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_sync)
        mock_crypto_sync.create_signature_from_object.return_value = valid_signature

        result = client.webhooks.verify(webhook)

        assert result == valid_webhook_data
        mock_crypto_sync.create_signature_from_object.assert_called_once()

    def test_verify_missing_data(self):
        """Test webhook verification fails when data is missing."""
        webhook_dict = {
            "code": "00",
            "desc": "success",
            "success": True,
            "data": None,
            "signature": "mock-signature",
        }

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        with pytest.raises(WebhookError, match="Webhook schema validation failed"):
            client.webhooks.verify(webhook_dict)

    def test_verify_missing_signature(self):
        """Test webhook verification fails when signature is missing."""
        valid_webhook_data = WebhookData(
            account_number="0123456789",
            amount=20000,
            description="thanh toan",
            reference="FT-REFERENCE",
            transaction_date_time="2025-12-12 09:00:00",
            virtual_account_number="",
            counter_account_bank_id="01202001",
            counter_account_bank_name="",
            counter_account_name="NGUYEN VAN A",
            counter_account_number="9876543210",
            virtual_account_name="",
            currency="VND",
            order_code=0,
            payment_link_id="payment-link-id",
            code="00",
            desc="success",
        )

        webhook = Webhook(
            code="00",
            desc="success",
            success=True,
            data=valid_webhook_data,
            signature="",
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        with pytest.raises(WebhookError, match="Invalid signature"):
            client.webhooks.verify(webhook)

    def test_verify_signature_mismatch(self, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch):
        """Test webhook verification fails when signature doesn't match."""
        valid_webhook_data = WebhookData(
            account_number="0123456789",
            amount=20000,
            description="thanh toan",
            reference="FT-REFERENCE",
            transaction_date_time="2025-12-12 09:00:00",
            virtual_account_number="",
            counter_account_bank_id="01202001",
            counter_account_bank_name="",
            counter_account_name="NGUYEN VAN A",
            counter_account_number="9876543210",
            virtual_account_name="",
            currency="VND",
            order_code=0,
            payment_link_id="payment-link-id",
            code="00",
            desc="success",
        )

        webhook = Webhook(
            code="00",
            desc="success",
            success=True,
            data=valid_webhook_data,
            signature="mock-signature",
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_sync)
        mock_crypto_sync.create_signature_from_object.return_value = "different-signature"

        with pytest.raises(WebhookError, match="Data not integrity"):
            client.webhooks.verify(webhook)

    def test_verify_crypto_returns_none(self, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch):
        """Test webhook verification fails when crypto provider returns None."""
        valid_webhook_data = WebhookData(
            account_number="0123456789",
            amount=20000,
            description="thanh toan",
            reference="FT-REFERENCE",
            transaction_date_time="2025-12-12 09:00:00",
            virtual_account_number="",
            counter_account_bank_id="01202001",
            counter_account_bank_name="",
            counter_account_name="NGUYEN VAN A",
            counter_account_number="9876543210",
            virtual_account_name="",
            currency="VND",
            order_code=0,
            payment_link_id="payment-link-id",
            code="00",
            desc="success",
        )

        webhook = Webhook(
            code="00",
            desc="success",
            success=True,
            data=valid_webhook_data,
            signature="mock-signature",
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_sync)
        mock_crypto_sync.create_signature_from_object.return_value = None

        with pytest.raises(WebhookError, match="Data not integrity"):
            client.webhooks.verify(webhook)

    def test_confirm_webhook_url(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test confirming webhook URL successfully."""
        valid_webhook_url = "https://example.com/webhook"
        expected_response = ConfirmWebhookResponse(
            webhook_url=valid_webhook_url,
            account_number="113366668888",
            account_name="QUY VAC XIN PHONG CHONG COVID",
            name="My Payment Channel",
            short_name="BIDV",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/confirm-webhook",
            method="POST",
            json={
                "code": "00",
                "desc": "success",
                "data": expected_response.model_dump(by_alias=True),
            },
            status_code=200,
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_sync)

        result = client.webhooks.confirm(valid_webhook_url)

        assert result.webhook_url == valid_webhook_url
        assert result.account_number == "113366668888"

    def test_confirm_empty_url(self):
        """Test confirming empty webhook URL fails."""
        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        with pytest.raises(WebhookError, match="Webhook URL invalid"):
            client.webhooks.confirm("")

    def test_confirm_validation_fails(
        self, httpx_mock: HTTPXMock, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test webhook confirmation fails when PayOS validation fails."""
        valid_webhook_url = "https://example.com/webhook"

        httpx_mock.add_response(
            url=f"{BASE_URL}/confirm-webhook",
            method="POST",
            json={"code": "20", "desc": "Webhook url invalid"},
            status_code=400,
        )

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_sync)

        with pytest.raises(WebhookError, match="Webhook validation failed"):
            client.webhooks.confirm(valid_webhook_url)

    # Tests for non-Webhook payload types
    def test_verify_valid_json_string_payload(
        self, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch
    ):
        """Test verifying webhook from valid JSON string payload."""
        import json

        valid_webhook_data = WebhookData(
            account_number="0123456789",
            amount=20000,
            description="thanh toan",
            reference="FT-REFERENCE",
            transaction_date_time="2025-12-12 09:00:00",
            virtual_account_number="",
            counter_account_bank_id="01202001",
            counter_account_bank_name="",
            counter_account_name="NGUYEN VAN A",
            counter_account_number="9876543210",
            virtual_account_name="",
            currency="VND",
            order_code=0,
            payment_link_id="payment-link-id",
            code="00",
            desc="success",
        )

        valid_signature = "mock-valid-signature"
        webhook_dict = {
            "code": "00",
            "desc": "success",
            "success": True,
            "data": valid_webhook_data.model_dump(by_alias=True),
            "signature": valid_signature,
        }
        json_string = json.dumps(webhook_dict)

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_sync)
        mock_crypto_sync.create_signature_from_object.return_value = valid_signature

        result = client.webhooks.verify(json_string)

        assert result == valid_webhook_data
        mock_crypto_sync.create_signature_from_object.assert_called_once()

    def test_verify_invalid_json_string(self):
        """Test webhook verification fails with invalid JSON string."""
        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        with pytest.raises(WebhookError, match="Invalid JSON"):
            client.webhooks.verify("not valid json")

    def test_verify_json_string_with_invalid_schema(self):
        """Test webhook verification fails when JSON string has invalid schema."""
        import json

        # Missing required 'data' field
        invalid_webhook = {"code": "00", "desc": "success", "signature": "sig"}
        json_string = json.dumps(invalid_webhook)

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        with pytest.raises(WebhookError, match="Webhook schema validation failed"):
            client.webhooks.verify(json_string)

    def test_verify_valid_bytes_payload(self, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch):
        """Test verifying webhook from valid JSON bytes payload."""
        import json

        valid_webhook_data = WebhookData(
            account_number="0123456789",
            amount=20000,
            description="thanh toan",
            reference="FT-REFERENCE",
            transaction_date_time="2025-12-12 09:00:00",
            virtual_account_number="",
            counter_account_bank_id="01202001",
            counter_account_bank_name="",
            counter_account_name="NGUYEN VAN A",
            counter_account_number="9876543210",
            virtual_account_name="",
            currency="VND",
            order_code=0,
            payment_link_id="payment-link-id",
            code="00",
            desc="success",
        )

        valid_signature = "mock-valid-signature"
        webhook_dict = {
            "code": "00",
            "desc": "success",
            "success": True,
            "data": valid_webhook_data.model_dump(by_alias=True),
            "signature": valid_signature,
        }
        json_bytes = json.dumps(webhook_dict).encode("utf-8")

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_sync)
        mock_crypto_sync.create_signature_from_object.return_value = valid_signature

        result = client.webhooks.verify(json_bytes)

        assert result == valid_webhook_data
        mock_crypto_sync.create_signature_from_object.assert_called_once()

    def test_verify_invalid_json_bytes(self):
        """Test webhook verification fails with invalid JSON bytes."""
        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        with pytest.raises(WebhookError, match="Invalid JSON"):
            client.webhooks.verify(b"not valid json bytes")

    def test_verify_valid_dict_payload(self, mock_crypto_sync, monkeypatch: pytest.MonkeyPatch):
        """Test verifying webhook from valid dict payload."""
        valid_webhook_data = WebhookData(
            account_number="0123456789",
            amount=20000,
            description="thanh toan",
            reference="FT-REFERENCE",
            transaction_date_time="2025-12-12 09:00:00",
            virtual_account_number="",
            counter_account_bank_id="01202001",
            counter_account_bank_name="",
            counter_account_name="NGUYEN VAN A",
            counter_account_number="9876543210",
            virtual_account_name="",
            currency="VND",
            order_code=0,
            payment_link_id="payment-link-id",
            code="00",
            desc="success",
        )

        valid_signature = "mock-valid-signature"
        webhook_dict = {
            "code": "00",
            "desc": "success",
            "success": True,
            "data": valid_webhook_data.model_dump(by_alias=True),
            "signature": valid_signature,
        }

        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_sync)
        mock_crypto_sync.create_signature_from_object.return_value = valid_signature

        result = client.webhooks.verify(webhook_dict)

        assert result == valid_webhook_data
        mock_crypto_sync.create_signature_from_object.assert_called_once()

    def test_verify_unsupported_payload_type(self):
        """Test webhook verification fails with unsupported payload type."""
        client = PayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        # Test with integer
        with pytest.raises(WebhookError, match="Unsupported payload type"):
            client.webhooks.verify(12345)  # type: ignore

        # Test with list
        with pytest.raises(WebhookError, match="Unsupported payload type"):
            client.webhooks.verify([1, 2, 3])  # type: ignore


class TestAsyncWebhooks:
    """Asynchronous tests for AsyncWebhooks."""

    @pytest.mark.asyncio
    async def test_verify_valid_webhook(self, mock_crypto_async, monkeypatch: pytest.MonkeyPatch):
        """Test verifying valid webhook with correct signature."""
        valid_webhook_data = WebhookData(
            account_number="0123456789",
            amount=20000,
            description="thanh toan",
            reference="FT-REFERENCE",
            transaction_date_time="2025-12-12 09:00:00",
            virtual_account_number="",
            counter_account_bank_id="01202001",
            counter_account_bank_name="",
            counter_account_name="NGUYEN VAN A",
            counter_account_number="9876543210",
            virtual_account_name="",
            currency="VND",
            order_code=0,
            payment_link_id="payment-link-id",
            code="00",
            desc="success",
        )

        valid_signature = "mock-valid-signature"
        webhook = Webhook(
            code="00",
            desc="success",
            success=True,
            data=valid_webhook_data,
            signature=valid_signature,
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_async)
        mock_crypto_async.create_signature_from_object.return_value = valid_signature

        result = await client.webhooks.verify(webhook)

        assert result == valid_webhook_data
        mock_crypto_async.create_signature_from_object.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_missing_data(self):
        """Test webhook verification fails when data is missing."""
        valid_webhook_data = WebhookData(
            account_number="0123456789",
            amount=20000,
            description="thanh toan",
            reference="FT-REFERENCE",
            transaction_date_time="2025-12-12 09:00:00",
            virtual_account_number="",
            counter_account_bank_id="01202001",
            counter_account_bank_name="",
            counter_account_name="NGUYEN VAN A",
            counter_account_number="9876543210",
            virtual_account_name="",
            currency="VND",
            order_code=0,
            payment_link_id="payment-link-id",
            code="00",
            desc="success",
        )

        # Directly manipulate the webhook object after creation
        webhook = Webhook(
            code="00",
            desc="success",
            success=True,
            data=valid_webhook_data,
            signature="mock-signature",
        )
        # Override data to None
        object.__setattr__(webhook, "data", None)

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        with pytest.raises(WebhookError, match="Invalid webhook data"):
            await client.webhooks.verify(webhook)

    @pytest.mark.asyncio
    async def test_verify_missing_signature(self):
        """Test webhook verification fails when signature is missing."""
        valid_webhook_data = WebhookData(
            account_number="0123456789",
            amount=20000,
            description="thanh toan",
            reference="FT-REFERENCE",
            transaction_date_time="2025-12-12 09:00:00",
            virtual_account_number="",
            counter_account_bank_id="01202001",
            counter_account_bank_name="",
            counter_account_name="NGUYEN VAN A",
            counter_account_number="9876543210",
            virtual_account_name="",
            currency="VND",
            order_code=0,
            payment_link_id="payment-link-id",
            code="00",
            desc="success",
        )

        webhook = Webhook(
            code="00",
            desc="success",
            success=True,
            data=valid_webhook_data,
            signature="",
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        with pytest.raises(WebhookError, match="Invalid signature"):
            await client.webhooks.verify(webhook)

    @pytest.mark.asyncio
    async def test_verify_signature_mismatch(
        self, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test webhook verification fails when signature doesn't match."""
        valid_webhook_data = WebhookData(
            account_number="0123456789",
            amount=20000,
            description="thanh toan",
            reference="FT-REFERENCE",
            transaction_date_time="2025-12-12 09:00:00",
            virtual_account_number="",
            counter_account_bank_id="01202001",
            counter_account_bank_name="",
            counter_account_name="NGUYEN VAN A",
            counter_account_number="9876543210",
            virtual_account_name="",
            currency="VND",
            order_code=0,
            payment_link_id="payment-link-id",
            code="00",
            desc="success",
        )

        webhook = Webhook(
            code="00",
            desc="success",
            success=True,
            data=valid_webhook_data,
            signature="mock-signature",
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_async)
        mock_crypto_async.create_signature_from_object.return_value = "different-signature"

        with pytest.raises(WebhookError, match="Data not integrity"):
            await client.webhooks.verify(webhook)

    @pytest.mark.asyncio
    async def test_verify_crypto_returns_none(
        self, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test webhook verification fails when crypto provider returns None."""
        valid_webhook_data = WebhookData(
            account_number="0123456789",
            amount=20000,
            description="thanh toan",
            reference="FT-REFERENCE",
            transaction_date_time="2025-12-12 09:00:00",
            virtual_account_number="",
            counter_account_bank_id="01202001",
            counter_account_bank_name="",
            counter_account_name="NGUYEN VAN A",
            counter_account_number="9876543210",
            virtual_account_name="",
            currency="VND",
            order_code=0,
            payment_link_id="payment-link-id",
            code="00",
            desc="success",
        )

        webhook = Webhook(
            code="00",
            desc="success",
            success=True,
            data=valid_webhook_data,
            signature="mock-signature",
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_async)
        mock_crypto_async.create_signature_from_object.return_value = None

        with pytest.raises(WebhookError, match="Data not integrity"):
            await client.webhooks.verify(webhook)

    @pytest.mark.asyncio
    async def test_confirm_webhook_url(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test confirming webhook URL successfully."""
        valid_webhook_url = "https://example.com/webhook"
        expected_response = ConfirmWebhookResponse(
            webhook_url=valid_webhook_url,
            account_number="113366668888",
            account_name="QUY VAC XIN PHONG CHONG COVID",
            name="My Payment Channel",
            short_name="BIDV",
        )

        httpx_mock.add_response(
            url=f"{BASE_URL}/confirm-webhook",
            method="POST",
            json={
                "code": "00",
                "desc": "success",
                "data": expected_response.model_dump(by_alias=True),
            },
            status_code=200,
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_async)

        result = await client.webhooks.confirm(valid_webhook_url)

        assert result.webhook_url == valid_webhook_url
        assert result.account_number == "113366668888"

    @pytest.mark.asyncio
    async def test_confirm_empty_url(self):
        """Test confirming empty webhook URL fails."""
        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        with pytest.raises(WebhookError, match="Webhook URL invalid"):
            await client.webhooks.confirm("")

    @pytest.mark.asyncio
    async def test_confirm_validation_fails(
        self, httpx_mock: HTTPXMock, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test webhook confirmation fails when PayOS validation fails."""
        valid_webhook_url = "https://example.com/webhook"

        httpx_mock.add_response(
            url=f"{BASE_URL}/confirm-webhook",
            method="POST",
            json={"code": "20", "desc": "Webhook url invalid"},
            status_code=400,
        )

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_async)

        with pytest.raises(WebhookError, match="Webhook validation failed"):
            await client.webhooks.confirm(valid_webhook_url)

    # Tests for non-Webhook payload types
    @pytest.mark.asyncio
    async def test_verify_valid_json_string_payload(
        self, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test verifying webhook from valid JSON string payload."""
        import json

        valid_webhook_data = WebhookData(
            account_number="0123456789",
            amount=20000,
            description="thanh toan",
            reference="FT-REFERENCE",
            transaction_date_time="2025-12-12 09:00:00",
            virtual_account_number="",
            counter_account_bank_id="01202001",
            counter_account_bank_name="",
            counter_account_name="NGUYEN VAN A",
            counter_account_number="9876543210",
            virtual_account_name="",
            currency="VND",
            order_code=0,
            payment_link_id="payment-link-id",
            code="00",
            desc="success",
        )

        valid_signature = "mock-valid-signature"
        webhook_dict = {
            "code": "00",
            "desc": "success",
            "success": True,
            "data": valid_webhook_data.model_dump(by_alias=True),
            "signature": valid_signature,
        }
        json_string = json.dumps(webhook_dict)

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_async)
        mock_crypto_async.create_signature_from_object.return_value = valid_signature

        result = await client.webhooks.verify(json_string)

        assert result == valid_webhook_data
        mock_crypto_async.create_signature_from_object.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_invalid_json_string(self):
        """Test webhook verification fails with invalid JSON string."""
        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        with pytest.raises(WebhookError, match="Invalid JSON"):
            await client.webhooks.verify("not valid json")

    @pytest.mark.asyncio
    async def test_verify_json_string_with_invalid_schema(self):
        """Test webhook verification fails when JSON string has invalid schema."""
        import json

        # Missing required 'data' field
        invalid_webhook = {"code": "00", "desc": "success", "signature": "sig"}
        json_string = json.dumps(invalid_webhook)

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        with pytest.raises(WebhookError, match="Webhook schema validation failed"):
            await client.webhooks.verify(json_string)

    @pytest.mark.asyncio
    async def test_verify_valid_bytes_payload(
        self, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test verifying webhook from valid JSON bytes payload."""
        import json

        valid_webhook_data = WebhookData(
            account_number="0123456789",
            amount=20000,
            description="thanh toan",
            reference="FT-REFERENCE",
            transaction_date_time="2025-12-12 09:00:00",
            virtual_account_number="",
            counter_account_bank_id="01202001",
            counter_account_bank_name="",
            counter_account_name="NGUYEN VAN A",
            counter_account_number="9876543210",
            virtual_account_name="",
            currency="VND",
            order_code=0,
            payment_link_id="payment-link-id",
            code="00",
            desc="success",
        )

        valid_signature = "mock-valid-signature"
        webhook_dict = {
            "code": "00",
            "desc": "success",
            "success": True,
            "data": valid_webhook_data.model_dump(by_alias=True),
            "signature": valid_signature,
        }
        json_bytes = json.dumps(webhook_dict).encode("utf-8")

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_async)
        mock_crypto_async.create_signature_from_object.return_value = valid_signature

        result = await client.webhooks.verify(json_bytes)

        assert result == valid_webhook_data
        mock_crypto_async.create_signature_from_object.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_invalid_json_bytes(self):
        """Test webhook verification fails with invalid JSON bytes."""
        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        with pytest.raises(WebhookError, match="Invalid JSON"):
            await client.webhooks.verify(b"not valid json bytes")

    @pytest.mark.asyncio
    async def test_verify_valid_dict_payload(
        self, mock_crypto_async, monkeypatch: pytest.MonkeyPatch
    ):
        """Test verifying webhook from valid dict payload."""
        valid_webhook_data = WebhookData(
            account_number="0123456789",
            amount=20000,
            description="thanh toan",
            reference="FT-REFERENCE",
            transaction_date_time="2025-12-12 09:00:00",
            virtual_account_number="",
            counter_account_bank_id="01202001",
            counter_account_bank_name="",
            counter_account_name="NGUYEN VAN A",
            counter_account_number="9876543210",
            virtual_account_name="",
            currency="VND",
            order_code=0,
            payment_link_id="payment-link-id",
            code="00",
            desc="success",
        )

        valid_signature = "mock-valid-signature"
        webhook_dict = {
            "code": "00",
            "desc": "success",
            "success": True,
            "data": valid_webhook_data.model_dump(by_alias=True),
            "signature": valid_signature,
        }

        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )
        monkeypatch.setattr(client, "crypto", mock_crypto_async)
        mock_crypto_async.create_signature_from_object.return_value = valid_signature

        result = await client.webhooks.verify(webhook_dict)

        assert result == valid_webhook_data
        mock_crypto_async.create_signature_from_object.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_unsupported_payload_type(self):
        """Test webhook verification fails with unsupported payload type."""
        client = AsyncPayOS(
            client_id=CLIENT_ID,
            api_key=API_KEY,
            checksum_key=CHECKSUM_KEY,
            base_url=BASE_URL,
        )

        # Test with integer
        with pytest.raises(WebhookError, match="Unsupported payload type"):
            await client.webhooks.verify(12345)  # type: ignore

        # Test with list
        with pytest.raises(WebhookError, match="Unsupported payload type"):
            await client.webhooks.verify([1, 2, 3])  # type: ignore
