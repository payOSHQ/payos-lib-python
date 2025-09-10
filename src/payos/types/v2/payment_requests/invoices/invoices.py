from typing import Optional

from ....._core.models import PayOSBaseModel


class Invoice(PayOSBaseModel):
    invoice_id: str
    invoice_number: Optional[str] = None
    issued_timestamp: Optional[int] = None
    issued_datetime: Optional[str] = None  # ISO date string
    transaction_id: Optional[str] = None
    reservation_code: Optional[str] = None
    code_of_tax: Optional[str] = None


class InvoicesInfo(PayOSBaseModel):
    invoices: list[Invoice]


class InvoiceRetrieveParams(PayOSBaseModel):
    payment_link_id: str


class InvoiceDownloadParams(PayOSBaseModel):
    payment_link_id: str


__all__ = [
    "Invoice",
    "InvoicesInfo",
    "InvoiceRetrieveParams",
    "InvoiceDownloadParams",
]
