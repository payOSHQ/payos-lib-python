import os
import httpx
from time import time
from dotenv import load_dotenv

from payos import PayOS

load_dotenv()

client = PayOS()

response = client.post(
    "/v2/payment-requests",
    body={
        "orderCode": int(time()),
        "amount": 2000,
        "description": "thanh toan",
        "returnUrl": "https://your-url.com/success",
        "cancelUrl": "https://your-url.com/cancel",
    },
    cast_to=dict,
    url="http://localhost:4006",
    signature_request="create-payment-link",
    signature_response="body",
)

print(response.get("checkoutUrl"))
