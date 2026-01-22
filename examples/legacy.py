"""Legacy API example - demonstrates v0.x compatibility with v1.x SDK.

Run with: python examples/legacy.py
"""

import os
import warnings
import time

# Set to "ignore" for cleaner output
warnings.filterwarnings("ignore", category=DeprecationWarning)

from payos import PayOS
from payos.type import PaymentData, ItemData
from payos.constants import ERROR_MESSAGE, ERROR_CODE
from payos.custom_error import PayOSError as LegacyPayOSError
from payos.utils import (
    convertObjToQueryStr,
    sortObjDataByKey,
    createSignatureFromObj,
    createSignatureOfPaymentRequest,
)


# Legacy constants
print(f"ERROR_MESSAGE: {ERROR_MESSAGE}")
print(f"ERROR_CODE: {ERROR_CODE}\n")

# Legacy error with (code, message) signature
legacy_error = LegacyPayOSError(code="20", message="Internal Server Error")

# Legacy types: PaymentData, ItemData
item = ItemData(name="Mi tom hao hao ly", quantity=1, price=1000)
payment_data = PaymentData(
    orderCode=int(time.time()),
    amount=1000,
    description="Thanh toan don hang",
    cancelUrl="http://localhost:8000/cancel",
    returnUrl="http://localhost:8000/success",
    items=[item],
    buyerName="Nguyen Van A",
    buyerEmail="test@example.com",
    buyerPhone="0123456789",
)
webhook_body = {
    "code": "00",
    "desc": "success",
    "success": True,
    "data": {
        "orderCode": 123,
        "amount": 3000,
        "description": "VQRIO123",
        "accountNumber": "12345678",
        "reference": "TF230204212323",
        "transactionDateTime": "2023-02-04 18:25:00",
        "currency": "VND",
        "paymentLinkId": "124c33293c43417ab7879e14c8d9eb18",
        "code": "00",
        "desc": "Thành công",
        "counterAccountBankId": "",
        "counterAccountBankName": "",
        "counterAccountName": "",
        "counterAccountNumber": "",
        "virtualAccountName": "",
        "virtualAccountNumber": "",
    },
    "signature": "",
}

# Legacy utils
test_key = "test_checksum_key"
sorted_obj = sortObjDataByKey({"b": 2, "a": 1})
query_str = convertObjToQueryStr({"amount": 1000, "orderCode": 123})
sig_from_obj = createSignatureFromObj({"amount": 1000}, test_key)
sig_payment = createSignatureOfPaymentRequest(payment_data, test_key)

# Initialize client
client_id = "your_client_id"
api_key = "your_api_key"
checksum_key = "your_checksum_key"

if all([client_id, api_key, checksum_key]):
    payOS = PayOS(client_id=client_id, api_key=api_key, checksum_key=checksum_key)

    try:
        # Legacy: createPaymentLink() -> New: payment_requests.create()
        result = payOS.createPaymentLink(payment_data)
        print(f"Created: {result.checkoutUrl}")
        print(f"to json: {result.to_json()}")

        # Legacy: getPaymentLinkInformation() -> New: payment_requests.get()
        info = payOS.getPaymentLinkInformation(payment_data.orderCode)
        print(f"Status: {info}")

        # Legacy: cancelPaymentLink() -> New: payment_requests.cancel()
        cancelled = payOS.cancelPaymentLink(payment_data.orderCode, "Test")
        print(f"Cancelled: {cancelled}")

        # Legacy: confirmWebhook() -> New: webhooks.confirm()
        webhook_response = payOS.confirmWebhook("https://your-domain.com/webhook")
        print(f"Webhook confirmed: {webhook_response}")

        # Legacy: verifyPaymentWebhookData() -> New: webhooks.verify()
        webhook_body["signature"] = createSignatureFromObj(webhook_body["data"], checksum_key)
        verified = payOS.verifyPaymentWebhookData(webhook_body)
        print(f"Webhook verified: {verified}")

    except LegacyPayOSError as e:
        print(f"Error: {e}")
else:
    print("Set PAYOS_CLIENT_ID, PAYOS_API_KEY, PAYOS_CHECKSUM_KEY to test API calls")
