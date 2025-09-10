import time

from dotenv import load_dotenv

from payos import APIError, PayOS
from payos.types import CreatePaymentLinkRequest, InvoiceRequest, ItemData

# Assume that credentials have been set in environment
# If not, you must provide them when init client
load_dotenv()


def sync_main() -> None:
    """
    Example demonstrating payment link creation with detailed item information
    This shows how to create professional invoices with multiple items and tax calculations
    The invoice only created if the payment gateway is connected to an invoice integration
    """
    client = PayOS()
    order_code = int(time.time())

    try:
        print("Creating payment link with detailed invoice...")

        # Detailed items breakdown
        items = [
            ItemData(
                name="iPhone 15 Pro Case",
                quantity=2,
                price=25000,
                unit="piece",
                tax_percentage=10,
            ),
            ItemData(
                name="Screen Protector",
                quantity=1,
                price=15000,
                unit="piece",
                tax_percentage=10,
            ),
            ItemData(
                name="Wireless Charger",
                quantity=1,
                price=50000,
                unit="piece",
                tax_percentage=10,
            ),
        ]

        # Invoice configuration
        invoice = InvoiceRequest(
            buyer_not_get_invoice=False,  # Customer wants invoice
            tax_percentage=10,  # Overall tax percentage
        )

        payment_data = CreatePaymentLinkRequest(
            order_code=order_code,
            amount=126500,  # Total amount including tax
            description=f"order{order_code}",
            return_url="https://your-website.com/payment/success",
            cancel_url="https://your-website.com/payment/cancel",
            # Buyer information
            buyer_name="Nguyen Van A",
            buyer_email="customer@example.com",
            buyer_phone="012456789",
            buyer_address="123 Nguyen Trai, District 1, Ho Chi Minh City",
            buyer_company_name="ABC Company Ltd.",
            buyer_tax_code="0123456789-001",
            # Detailed items breakdown
            items=items,
            # Invoice configuration
            invoice=invoice,
            expired_at=int(time.time()) + 60 * 60,  # Expired in 1 hour
        )

        payment_link = client.payment_requests.create(payment_data=payment_data)

        print("Payment link created successfully!")
        print()
        print("Payment Details:")
        print(f"   Order Code: {payment_link.order_code}")
        print(f"   Payment Link ID: {payment_link.payment_link_id}")
        print(f"   Total Amount: {payment_link.amount:,} VND")
        print()
        print("   Checkout URL:")
        print(f"   {payment_link.checkout_url}")
        print()
        print("   QR Code:")
        print(f"   {payment_link.qr_code}")
        print()

    except APIError as error:
        print("   Failed to create payment link:")
        print(f"   Status: {error.status_code}")
        print(f"   Message: {error.error_desc}")
        print(f"   Code: {error.error_code}")

        # Handle specific error cases
        if error.status_code == 400:
            print("     Check your payment data format and required fields")
        elif error.status_code == 401:
            print("     Verify your PayOS API credentials")
    except Exception as error:
        print(f"   Unexpected error: {error}")


if __name__ == "__main__":
    sync_main()
