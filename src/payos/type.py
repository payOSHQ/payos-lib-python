"""Legacy type module for backward compatibility with v0.x.

.. deprecated:: 1.0.0
    Import from 'payos.types' instead. This module will be removed in v2.0.0.

"""

import warnings
from dataclasses import dataclass
from typing import Any, Optional

warnings.warn(
    "The 'payos.type' module is deprecated and will be removed in v2.0.0. "
    "Use 'payos.types' instead.",
    DeprecationWarning,
    stacklevel=2,
)


class ItemData:
    def __init__(self, name: str, quantity: int, price: int):
        self.name = name
        self.quantity = quantity
        self.price = price

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "quantity": self.quantity,
            "price": self.price,
        }


class PaymentData:
    def __init__(
        self,
        orderCode: int,
        amount: int,
        description: str,
        cancelUrl: str,
        returnUrl: str,
        buyerName: Optional[str] = None,
        items: Optional[list[ItemData]] = None,
        buyerEmail: Optional[str] = None,
        buyerPhone: Optional[str] = None,
        buyerAddress: Optional[str] = None,
        expiredAt: Optional[int] = None,
        signature: Optional[str] = None,
    ):
        self.orderCode = orderCode
        self.amount = amount
        self.description = description
        self.items = items
        self.cancelUrl = cancelUrl
        self.returnUrl = returnUrl
        self.signature = signature
        self.buyerName = buyerName
        self.buyerEmail = buyerEmail
        self.buyerPhone = buyerPhone
        self.buyerAddress = buyerAddress
        self.expiredAt = expiredAt

    def to_json(self) -> dict[str, Any]:
        return {
            "orderCode": self.orderCode,
            "amount": self.amount,
            "description": self.description,
            "items": [item.to_json() for item in self.items] if self.items else None,
            "cancelUrl": self.cancelUrl,
            "returnUrl": self.returnUrl,
            "signature": self.signature,
            "buyerName": self.buyerName,
            "buyerEmail": self.buyerEmail,
            "buyerPhone": self.buyerPhone,
            "buyerAddress": self.buyerAddress,
            "expiredAt": self.expiredAt,
        }


@dataclass
class CreatePaymentResult:
    bin: str
    accountNumber: str
    accountName: str
    amount: int
    description: str
    orderCode: int
    currency: str
    paymentLinkId: str
    status: str
    checkoutUrl: str
    qrCode: str
    expiredAt: Optional[int] = None

    def to_json(self) -> dict[str, Any]:
        return {
            "bin": self.bin,
            "accountNumber": self.accountNumber,
            "accountName": self.accountName,
            "amount": self.amount,
            "description": self.description,
            "orderCode": self.orderCode,
            "currency": self.currency,
            "paymentLinkId": self.paymentLinkId,
            "status": self.status,
            "expiredAt": self.expiredAt,
            "checkoutUrl": self.checkoutUrl,
            "qrCode": self.qrCode,
        }


@dataclass
class Transaction:
    reference: str
    amount: int
    accountNumber: str
    description: str
    transactionDateTime: str
    virtualAccountName: Optional[str]
    virtualAccountNumber: Optional[str]
    counterAccountBankId: Optional[str]
    counterAccountBankName: Optional[str]
    counterAccountName: Optional[str]
    counterAccountNumber: Optional[str]

    def to_json(self) -> dict[str, Any]:
        return {
            "reference": self.reference,
            "amount": self.amount,
            "accountNumber": self.accountNumber,
            "description": self.description,
            "transactionDateTime": self.transactionDateTime,
            "virtualAccountName": self.virtualAccountName,
            "virtualAccountNumber": self.virtualAccountNumber,
            "counterAccountBankId": self.counterAccountBankId,
            "counterAccountBankName": self.counterAccountBankName,
            "counterAccountName": self.counterAccountName,
            "counterAccountNumber": self.counterAccountNumber,
        }


@dataclass
class PaymentLinkInformation:
    id: str
    orderCode: int
    amount: int
    amountPaid: int
    amountRemaining: int
    status: str
    createdAt: str
    transactions: list[Transaction]
    cancellationReason: Optional[str]
    canceledAt: Optional[str]

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "orderCode": self.orderCode,
            "amount": self.amount,
            "amountPaid": self.amountPaid,
            "amountRemaining": self.amountRemaining,
            "status": self.status,
            "createdAt": self.createdAt,
            "transactions": [t.to_json() for t in self.transactions] if self.transactions else None,
            "cancellationReason": self.cancellationReason,
            "canceledAt": self.canceledAt,
        }


@dataclass
class WebhookData:
    orderCode: int
    amount: int
    description: str
    accountNumber: str
    reference: str
    transactionDateTime: str
    paymentLinkId: str
    code: str
    desc: str
    counterAccountBankId: Optional[str]
    counterAccountBankName: Optional[str]
    counterAccountName: Optional[str]
    counterAccountNumber: Optional[str]
    virtualAccountName: Optional[str]
    virtualAccountNumber: Optional[str]
    currency: str

    def to_json(self) -> dict[str, Any]:
        return {
            "orderCode": self.orderCode,
            "amount": self.amount,
            "description": self.description,
            "accountNumber": self.accountNumber,
            "reference": self.reference,
            "transactionDateTime": self.transactionDateTime,
            "paymentLinkId": self.paymentLinkId,
            "currency": self.currency,
            "code": self.code,
            "desc": self.desc,
            "counterAccountBankId": self.counterAccountBankId,
            "counterAccountBankName": self.counterAccountBankName,
            "counterAccountName": self.counterAccountName,
            "counterAccountNumber": self.counterAccountNumber,
            "virtualAccountName": self.virtualAccountName,
            "virtualAccountNumber": self.virtualAccountNumber,
        }


__all__ = [
    "ItemData",
    "PaymentData",
    "CreatePaymentResult",
    "Transaction",
    "PaymentLinkInformation",
    "WebhookData",
]
