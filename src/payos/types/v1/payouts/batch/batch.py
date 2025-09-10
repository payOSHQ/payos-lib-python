from typing import Optional

from ....._core.models import PayOSBaseModel


class PayoutBatchItem(PayOSBaseModel):
    reference_id: str
    amount: int
    description: str
    to_bin: str
    to_account_number: str


class PayoutBatchRequest(PayOSBaseModel):
    reference_id: str
    validate_destination: bool = False
    category: Optional[list[str]] = None
    payouts: list[PayoutBatchItem]


class BatchPayout(PayOSBaseModel):
    id: str
    reference_id: str
    amount: int
    status: str
    validate_destination: bool
    category: Optional[list[str]] = None
    payouts: list[PayoutBatchItem]
    created_at: str
    updated_at: str


__all__ = ["PayoutBatchItem", "PayoutBatchRequest", "BatchPayout"]
