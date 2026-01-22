# Migration guide

This guide outlines the changes and steps needed to migrate your codebase to the latest version of payOS Python SDK.

## Breaking change

### Method name

All method related to payment requests now under `PayOS.payment_requests` or `AsyncPayOS.payment_requests`.

```python
# before
client.createPaymentLink(request_data)
client.getPaymentLinkInformation(id)
client.cancelPaymentLink(id, cancellation_reason)

# after
client.payment_requests.create(request_data)
client.payment_requests.get(id)
client.payment_requests.cancel(id, cancellation_reason)
```

For webhook methods, they now under `PayOS.webhooks` or `AsyncPayOS.webhooks`.

```python
# before
client.confirmWebhook("https://your-webhook.com")
client.verifyPaymentWebhookData(webhook)

# after
client.webhooks.confirm("https://your-webhook.com")
client.webhooks.verify(webhook)
```

### Types

Some types has been renamed, more details below.

```python
# before
payment_data: PaymentData = ...
result: CreatePaymentResult = client.createPaymentLink(payment_data)

# after
payment_data: CreatePaymentLinkRequest = ...
result: CreatePaymentLinkResponse = client.payment_requests.create(payment_data)
```

```python
# before
payment_link_info: PaymentLinkInformation = client.getPaymentLinkInformation(id)
payment_link_cancelled: PaymentLinkInformation = client.cancelPaymentLink(id, cancellation_reason)

# after
payment_link_info: PaymentLink = client.payment_requests.get(id)
payment_link_cancelled: PaymentLink = client.payment_requests.cancel(id, cancellation_reason)
```

```python
# before
confirm_result: str = client.confirmWebhook("https://your-webhook.com")

# after
confirm_result: ConfirmWebhookResponse = client.webhooks.confirm("https://your-webhook.com")
```

### Attribute naming convention

v0.x uses **camelCase** for all type attributes. v1.x uses **snake_case** for all type attributes.

```python
# before (v0.x - camelCase)
result.checkoutUrl
result.orderCode
result.paymentLinkId
payment_link.amountPaid
payment_link.createdAt
webhook_data.transactionDateTime

# after (v1.x - snake_case)
result.checkout_url
result.order_code
result.payment_link_id
payment_link.amount_paid
payment_link.created_at
webhook_data.transaction_date_time
```

### `to_json()` method behavior change

The `to_json()` method behavior has changed between v0.x and v1.x:

| Version | `to_json()` returns | Key format |
| ------- | ------------------- | ---------- |
| v0.x    | `dict`              | camelCase  |
| v1.x    | `str` (JSON string) | snake_case |

```python
# before (v0.x) - returns dict with camelCase keys
result = client.createPaymentLink(payment_data)
json_dict = result.to_json()  # Returns: {"orderCode": 123, "checkoutUrl": "...", ...}
type(json_dict)  # <class 'dict'>

# after (v1.x) - returns JSON string with snake_case keys
result = client.payment_requests.create(payment_data)
json_str = result.to_json()  # Returns: '{"order_code": 123, "checkout_url": "...", ...}'
type(json_str)  # <class 'str'>
```

To get equivalent v0.x behavior in v1.x, use `model_dump_camel_case()`:

```python
# v1.x - get dict with camelCase keys (equivalent to v0.x to_json())
result = client.payment_requests.create(payment_data)
json_dict = result.model_dump_camel_case()  # Returns: {"orderCode": 123, "checkoutUrl": "...", ...}
type(json_dict)  # <class 'dict'>

# v1.x - other serialization options
result.model_dump()                    # dict with snake_case keys
result.model_dump(by_alias=True)       # dict with camelCase keys (same as model_dump_camel_case)
result.model_dump_snake_case()         # dict with snake_case keys (same as model_dump)
result.model_dump_json()               # JSON string with snake_case keys (same as to_json)
result.model_dump_json(by_alias=True)  # JSON string with camelCase keys
```

### Handling errors

The library now raise exception as `PayOSError`, API related errors as `APIError`, webhook related errors as `WebhookError` and signature related errors as `InvalidSignatureError` instead of raise `PayOSError` for related API errors and `Error` for other errors.

```python
# before
try:
    result = client.createPaymentLink(payment_data)
except PayOSError as e:
    print(e)


# after
try:
    result = client.payment_requests.create(payment_data)
except APIError as e:
    print(e)
```

## Backward compatibility layer

v1.x includes a backward compatibility layer that allows v0.x code to work with deprecation warnings. This gives you time to migrate gradually.

### Using the compatibility layer

Your existing v0.x code will continue to work:

```python
from payos import PayOS
from payos.type import PaymentData, ItemData

client = PayOS(client_id, api_key, checksum_key)

# v0.x style - still works with deprecation warnings
item = ItemData(name="Product", quantity=1, price=1000)
payment_data = PaymentData(
    orderCode=123,
    amount=1000,
    description="Order",
    cancelUrl="http://cancel",
    returnUrl="http://return",
    items=[item],
)

# Legacy methods return the exact same types as v0.x
result = client.createPaymentLink(payment_data)
print(result.checkoutUrl)  # camelCase works
print(result.to_json())    # Returns dict with camelCase keys (v0.x behavior)

info = client.getPaymentLinkInformation(123)
print(info.orderCode)      # camelCase works
print(info.amountPaid)     # camelCase works

# Legacy methods also throw the same errors as v0.x
from payos.custom_error import PayOSError
try:
    result = client.createPaymentLink(payment_data)
except PayOSError as e:
    print(e.code, e.message)  # Same error interface as v0.x
```

We recommend migrating to the new API before v2.0.0 release.
