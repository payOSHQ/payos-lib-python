from typing import Literal, Optional

from ...._core.models import PayOSBaseModel

TaxPercentage = Literal[-2, -1, 0, 5, 10]


class ItemData(PayOSBaseModel):
    name: str
    quantity: int
    price: int
    unit: Optional[str] = None
    tax_percentage: Optional[TaxPercentage] = None


class InvoiceRequest(PayOSBaseModel):
    buyer_not_get_invoice: Optional[bool] = None
    tax_percentage: Optional[TaxPercentage] = None


class Transaction(PayOSBaseModel):
    reference: str
    amount: int
    account_number: str
    description: str
    transaction_date_time: str
    virtual_account_name: Optional[str] = None
    virtual_account_number: Optional[str] = None
    counter_account_bank_id: Optional[str] = None
    counter_account_bank_name: Optional[str] = None
    counter_account_name: Optional[str] = None
    counter_account_number: Optional[str] = None


PaymentLinkStatus = Literal[
    "PENDING", "CANCELLED", "UNDERPAID", "PAID", "EXPIRED", "PROCESSING", "FAILED"
]


class CreatePaymentLinkRequest(PayOSBaseModel):
    order_code: int
    amount: int
    description: str
    cancel_url: str
    return_url: str
    signature: Optional[str] = None
    items: Optional[list[ItemData]] = None
    buyer_name: Optional[str] = None
    buyer_company_name: Optional[str] = None
    buyer_tax_code: Optional[str] = None
    buyer_email: Optional[str] = None
    buyer_phone: Optional[str] = None
    buyer_address: Optional[str] = None
    invoice: Optional[InvoiceRequest] = None
    expired_at: Optional[int] = None


class CreatePaymentLinkResponse(PayOSBaseModel):
    bin: str
    account_number: str
    account_name: str
    amount: int
    description: str
    order_code: int
    currency: str
    payment_link_id: str
    status: PaymentLinkStatus
    expired_at: Optional[int] = None
    checkout_url: str
    qr_code: str


class CancelPaymentLinkRequest(PayOSBaseModel):
    cancellation_reason: Optional[str] = None


class PaymentLink(PayOSBaseModel):
    id: str
    order_code: int
    amount: int
    amount_paid: int
    amount_remaining: int
    status: PaymentLinkStatus
    created_at: str
    transactions: list[Transaction]
    cancellation_reason: Optional[str] = None
    canceled_at: Optional[str] = None


__all__ = [
    "TaxPercentage",
    "ItemData",
    "InvoiceRequest",
    "Transaction",
    "PaymentLinkStatus",
    "CreatePaymentLinkRequest",
    "CreatePaymentLinkResponse",
    "CancelPaymentLinkRequest",
    "PaymentLink",
]
