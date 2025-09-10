# payOS Python SDK

[![PyPI version](<https://img.shields.io/pypi/v/payos.svg?label=pypi%20(stable)>)](https://pypi.org/project/payos/)

The payOS Python library provides convenient access to the payOS Merchant API from applications written in Python. The library includes type definitions for all request params and response fields, and offers both synchronous and asynchronous clients powered by [httpx](https://github.com/encode/httpx).

To learn how to use payOS Merchant API, checkout our [API Reference](https://payos.vn/docs/api) and [Documentation](https://payos.vn/docs). We also have some examples in [Examples](./examples/).

## Requirements

Python 3.9 or higher.

## Installation

```bash
# install from PyPi
pip install payos
```

> [!IMPORTANT]
> If update from v0, check [Migration guide](./MIGRATION.md) for detail migration.

## Usage

### Basic usage

First you need to initialize the client to interacting with payOS Merchant API.

```python
from payos import PayOS

client = PayOS(
    client_id=os.getenv("PAYOS_CLIENT_ID"),
    api_key=os.getenv("PAYOS_API_KEY"),
    checksum_key=os.getenv("PAYOS_CHECKSUM_KEY"),
    # ... other options
)
```

Then you can interact with payOS Merchant API, example create a payment link using `payment_requests.create()`.

```python
from payos.types import CreatePaymentLinkRequest

response = client.payment_requests.create(payment_data=CreatePaymentLinkRequest(
    order_code=int(time.time()),
    amount=2000,
    description="Thanh toan",
    cancel_url="https://your-url.com/cancel",
    return_url="https://your-url.com/success",
))
```

### Webhook verification

You can register an endpoint to receive the payment webhook.

```python
confirm_result = client.webhooks.confirm('https://your-url.com/webhooks')
```

Then using `webhooks.verify()` to verify and receive webhook data.

```python
# example using flask, more details in ./examples/webhooks_handling.py
@app.route("/webhooks", methods=["POST"])
def webhooks():
    data = request.get_data()

    try:
        webhook_data = client.webhooks.verify(data)
    except WebhookError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"error": None, "data": webhook_data.model_dump_camel_case()})
```

For more information about webhooks, see [the API doc](https://payos.vn/docs/api/#tag/payment-webhook/operation/payment-webhook).

### Handling errors

When the API return a non-success status code(i.e, 4xx or 5xx response) or non-success code data (any code except '00'), a subclass of `payos.APIError` is raised.

```python
try:
    response = client.payment_requests.create(payment_data=payment_data)
    print(response)
except APIError as e:
    print(e.error_code)
    print(e.error_desc)
    print(e.status_code)
```

### Asynchronous usage

Simply import `AsyncPayOS` instead of `PayOS` and use `await` with each API call:

```python
import asyncio

from payos import AsyncPayOS
from payos.types import CreatePaymentLinkRequest

async def main() -> None:
    client = AsyncPayOS()
    payment_data = CreatePaymentLinkRequest(
        order_code=int(time.time()),
        amount=2000,
        description="Thanh toan",
        cancel_url="https://your-url.com/cancel",
        return_url="https://your-url.com/success",
    )
    try:
        response = await client.payment_requests.create(payment_data=payment_data)
        print(response)
    except APIError as e:
        print(e)

asyncio.run(main())
```

### Auto pagination

List method in the payOS Merchant API are paginated, the library provides auto-paginating iterators with each response.

```python
import os

from payos import PayOS
from payos.types import GetPayoutListParams

client = PayOS(
    client_id=os.getenv("PAYOS_PAYOUT_CLIENT_ID"),
    api_key=os.getenv("PAYOS_PAYOUT_API_KEY"),
    checksum_key=os.getenv("PAYOS_PAYOUT_CHECKSUM_KEY"),
)


def main() -> None:
    payouts = []
    for payout in client.payouts.list(GetPayoutListParams(limit=3)):
        payouts.append(payout)
    # or
    payouts_data = client.payouts.list(GetPayoutListParams(limit=3))
    payouts = payout_data.to_list()

    print(payouts)


main()

```

Or asynchronous:

```python
import asyncio
import os

from payos import AsyncPayOS
from payos.types import GetPayoutListParams

client = AsyncPayOS(
    client_id=os.getenv("PAYOS_PAYOUT_CLIENT_ID"),
    api_key=os.getenv("PAYOS_PAYOUT_API_KEY"),
    checksum_key=os.getenv("PAYOS_PAYOUT_CHECKSUM_KEY"),
)


async def main() -> None:
    payouts = []
    async for payout in await client.payouts.list(GetPayoutListParams(limit=3)):
        payouts.append(payout)
    # or
    payouts_data = await client.payouts.list(GetPayoutListParams(limit=3))
    payouts = await payouts_data.to_list()

    print(payouts)


asyncio.run(main())

```

Alternative, you can use the `.has_next_page()`, `.get_next_page()` methods for more control:

```python
# remove `await` for non-async usage
first_page = await client.payouts.list(GetPayoutListParams(limit=3))
if first_page.has_next_page():
    next_page = await first_page.get_next_page()
    print(f"number of items we just fetched: {len(next_page.data)}")
```

Or just work directly with the returned data:

```python
# remove `await` for non-async usage
first_page = await client.payouts.list(GetPayoutListParams(limit=3))
for payout in first_page.data:
    print(payout.id)
```

### Advanced usage

#### Custom configuration

You can customize the PayOS client with various options:

```python
import os
import httpx

from payos import PayOS

client = PayOS(
    client_id=os.getenv("PAYOS_CLIENT_ID"),
    api_key=os.getenv("PAYOS_API_KEY"),
    checksum_key=os.getenv("PAYOS_CHECKSUM_KEY"),
    timeout=15.0,
    max_retries=4,
    http_client=httpx.Client(
        proxy="http://my-proxy.com", transport=httpx.HTTPTransport(local_address="0.0.0.0")
    ),
)
```

#### Request-level options

You can override client-level settings for individual requests:

```python
from payos import PayOS

client = PayOS()

client.payment_requests.get(1757060811, timeout=2, max_retries=0)
```

#### Logging

We use standard library [`logging`](https://docs.python.org/3/library/logging.html) module. You can enable logging by setting the environment variable `PAYOS_LOG` to `info` or `debug`.

```bash
export PAYOS_LOG=info
```

#### Direct API access

For advanced use cases, you can make direct API calls:

```python
from payos import PayOS

client = PayOS()

response = client.get("/v2/payment-requests", cast_to=dict)

response = client.post(
    "/v2/payment-requests",
    body={
        "orderCode": int(time()),
        "amount": 2000,
        "description": "thanh toan",
        "returnUrl": "https://your-url.com/success",
        "cancelUrl": "https://your-url.com/cancel",
        "signature": "signature",
    },
    cast_to=dict,
)
```

#### Signature

The signature can be manually created by `.crypto`:

```python
# for create payment link signature
signature = client.crypto.create_signature_of_payment_request(
    {
        "orderCode": int(time()),
        "amount": 2000,
        "description": "thanh toan",
        "returnUrl": "https://your-url.com/success",
        "cancelUrl": "https://your-url.com/cancel",
    },
    client.checksum_key,
)

# for payment-requests and webhook signature
signature = client.crypto.create_signature_from_object(
    data,
    client.checksum_key,
)

# for payouts signature
signature = client.crypto.create_signature(client.checksum_key, data)
```

## Contributing

See [the contributing documentation](./CONTRIBUTING.md).
