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
