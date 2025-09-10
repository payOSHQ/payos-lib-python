"""Payment requests resource module for payOS API v2."""

from .payment_requests import AsyncPaymentRequests, PaymentRequests

__all__ = ["PaymentRequests", "AsyncPaymentRequests"]
