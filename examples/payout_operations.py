import os
import time
from pprint import pprint

from dotenv import load_dotenv

from payos import APIError, PayOS
from payos.types import GetPayoutListParams, PayoutBatchItem, PayoutBatchRequest

load_dotenv()


def sync_main() -> None:
    """
    Example demonstrating payout operations (synchronous).
    Note: Payout credentials are different from payment request credentials.
    """
    # Initialize PayOS client with payout credentials
    client = PayOS(
        client_id=os.getenv("PAYOS_PAYOUT_CLIENT_ID"),
        api_key=os.getenv("PAYOS_PAYOUT_API_KEY"),
        checksum_key=os.getenv("PAYOS_PAYOUT_CHECKSUM_KEY"),
    )

    try:
        print("Creating a batch payout...")
        reference_id = f"payout_{int(time.time())}"

        # Create payout batch items
        payout_items = [
            PayoutBatchItem(
                reference_id=f"{reference_id}_0",
                amount=2000,
                description="batch payout",
                to_bin="970422",
                to_account_number="0123456789",
            ),
            PayoutBatchItem(
                reference_id=f"{reference_id}_1",
                amount=2000,
                description="batch payout",
                to_bin="970422",
                to_account_number="0123456789",
            ),
            PayoutBatchItem(
                reference_id=f"{reference_id}_2",
                amount=2000,
                description="batch payout",
                to_bin="970422",
                to_account_number="0123456789",
            ),
        ]

        # Create batch payout request
        payout_batch_request = PayoutBatchRequest(
            reference_id=reference_id,
            category=["salary"],
            validate_destination=True,
            payouts=payout_items,
        )

        # Create the batch payout
        payout_batch = client.payouts.batch.create(payout_batch_request)
        print("Payout detail:")
        pprint(payout_batch)

        print("\nFetching recent payouts...")
        # List recent payouts
        payouts_page = client.payouts.list(params=GetPayoutListParams(limit=3, offset=6))
        payouts = payouts_page.to_list()

        if len(payouts) == 0:
            print("No payouts found")
        else:
            print("Payouts retrieved:")
            pprint(payouts)

        print("\nFetching payout account balance...")
        # Get account balance
        account_info = client.payouts_account.balance()

        print("Account Information:")
        pprint(account_info)

    except APIError as error:
        print(f"API Error: {error}")
        print(f"Status Code: {error.status_code}")
        print(f"Error Code: {error.error_code}")
        print(f"Error Description: {error.error_desc}")
    except Exception as error:
        print(f"Unexpected error: {error}")


if __name__ == "__main__":
    sync_main()
