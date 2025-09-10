"""payOS API v2 resources."""

from .payment_requests import AsyncPaymentRequests, PaymentRequests

__all__ = ["PaymentRequests", "AsyncPaymentRequests"]
