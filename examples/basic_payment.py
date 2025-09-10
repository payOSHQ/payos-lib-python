import asyncio
import time
from pprint import pprint

from dotenv import load_dotenv

from payos import APIError, AsyncPayOS, PayOS
from payos.types import CreatePaymentLinkRequest

# Assume that credentials have been set in environment
# If not, you must provide them when init client
load_dotenv()


def sync_main() -> None:
    client = PayOS()
    payment_data = CreatePaymentLinkRequest(
        order_code=int(time.time()),
        amount=2000,
        description="Thanh toan",
        cancel_url="https://your-url.com/cancel",
        return_url="https://your-url.com/success",
    )
    try:
        response = client.payment_requests.create(payment_data=payment_data)
        pprint(response)
    except APIError as e:
        pprint(e.error_code)
        pprint(e.error_desc)
        pprint(e.status_code)


async def async_main() -> None:
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
        pprint(response)
    except APIError as e:
        pprint(e)


if __name__ == "__main__":
    sync_main()

    asyncio.run(async_main())
