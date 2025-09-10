from typing import Optional

from ..._core.models import PayOSBaseModel


class WebhookData(PayOSBaseModel):
    order_code: int
    amount: int
    description: str
    account_number: str
    reference: str
    transaction_date_time: str
    currency: str
    payment_link_id: str
    code: str
    desc: str
    counter_account_bank_id: Optional[str] = None
    counter_account_bank_name: Optional[str] = None
    counter_account_name: Optional[str] = None
    counter_account_number: Optional[str] = None
    virtual_account_name: Optional[str] = None
    virtual_account_number: Optional[str] = None


class Webhook(PayOSBaseModel):
    code: str
    desc: str
    success: Optional[bool] = None
    data: WebhookData
    signature: str


class ConfirmWebhookRequest(PayOSBaseModel):
    webhook_url: str


class ConfirmWebhookResponse(PayOSBaseModel):
    webhook_url: str
    account_name: str
    account_number: str
    name: str
    short_name: str


__all__ = [
    "WebhookData",
    "Webhook",
    "ConfirmWebhookRequest",
    "ConfirmWebhookResponse",
]
