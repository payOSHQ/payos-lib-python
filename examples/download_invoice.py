import os
from dotenv import load_dotenv
from payos import PayOS, APIError

load_dotenv()

client = PayOS()


def download_invoice(payment_link_id: str, invoice_id: str):
    try:
        file_response = client.payment_requests.invoices.download(invoice_id, payment_link_id)
        download_dir = "./examples/downloads"
        os.makedirs(download_dir, exist_ok=True)
        if file_response.filename:
            filepath = file_response.save_to_directory(download_dir)
        else:
            filepath = os.path.join(download_dir, f"invoice_{invoice_id}.pdf")
            file_response.save_to_file(filepath)
        print(f"Download to: {filepath}")
        print(f"Size: {file_response.size:,} bytes")
    except APIError as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def main() -> None:
    payment_link_id = "b9253e3efd8a4196b521fe3eb0808478"
    try:
        invoices_info = client.payment_requests.invoices.get(payment_link_id)
        print(f"Retrieve {len(invoices_info.invoices)} invoices")
        for invoice in invoices_info.invoices:
            print(f"Invoice ID: {invoice.invoice_id}")

            if invoice.code_of_tax:
                download_invoice(payment_link_id, invoice.invoice_id)
    except APIError as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
