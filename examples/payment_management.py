import time

from dotenv import load_dotenv

from payos import NotFoundError, PayOS
from payos.types import CreatePaymentLinkRequest

# Assume that credentials have been set in environment
# If not, you must provide them when init client
load_dotenv()


def main() -> None:
    client = PayOS()
    order_code = int(time.time())

    try:
        # First, create a payment link
        print("Creating payment link...")
        payment_data = CreatePaymentLinkRequest(
            order_code=order_code,
            amount=25000,
            description="demo",
            return_url="https://your-website.com/success",
            cancel_url="https://your-website.com/cancel",
        )

        payment_link = client.payment_requests.create(payment_data=payment_data)
        print(f"Payment created with ID: {payment_link.payment_link_id}")

        # Retrieve payment information using order code
        print("\nRetrieving payment info by order code...")
        retrieved_payment = client.payment_requests.get(order_code)
        print(f"Status: {retrieved_payment.status}")
        print(f"Amount: {retrieved_payment.amount:,} VND")
        print(f"Amount Paid: {retrieved_payment.amount_paid:,} VND")
        print(f"Created At: {retrieved_payment.created_at}")

        # Show additional payment details
        print(f"Amount Remaining: {retrieved_payment.amount_remaining:,} VND")
        print(f"Order Code: {retrieved_payment.order_code}")
        print(f"Payment ID: {retrieved_payment.id}")

        # Cancel the payment
        print("\nCancelling payment...")
        cancelled_payment = client.payment_requests.cancel(
            order_code, cancellation_reason="Demo cancellation"
        )

        print("Payment cancelled successfully")
        print(f"New status: {cancelled_payment.status}")
        print(f"Cancellation reason: {cancelled_payment.cancellation_reason}")
        if cancelled_payment.canceled_at:
            print(f"Cancelled at: {cancelled_payment.canceled_at}")

    except NotFoundError as error:
        print("Error details:")
        print(f"   Status: {error.status_code}")
        print(f"   Message: {error.error_desc}")
        print(f"   Code: {error.error_code}")
    except Exception as error:
        print(f"Unexpected error: {error}")


if __name__ == "__main__":
    main()
