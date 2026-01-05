from typing import Literal, Optional

from ...._core.models import PayOSBaseModel
from ...._core.pagination import Pagination

PayoutTransactionState = Literal[
    "RECEIVED", "PROCESSING", "CANCELLED", "SUCCEEDED", "ON_HOLD", "REVERSED", "FAILED"
]

PayoutApprovalState = Literal[
    "DRAFTING",
    "SUBMITTED",
    "APPROVED",
    "REJECTED",
    "CANCELLED",
    "SCHEDULED",
    "PROCESSING",
    "FAILED",
    "PARTIAL_COMPLETED",
    "COMPLETED",
]


class PayoutRequest(PayOSBaseModel):
    reference_id: str
    amount: int
    description: str
    to_bin: str
    to_account_number: str
    category: Optional[list[str]] = None


class PayoutTransaction(PayOSBaseModel):
    id: str
    reference_id: str
    amount: int
    description: str
    to_bin: str
    to_account_number: str
    to_account_name: Optional[str] = None
    reference: Optional[str] = None
    transaction_datetime: Optional[str] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    state: PayoutTransactionState


class Payout(PayOSBaseModel):
    id: str
    reference_id: str
    transactions: list[PayoutTransaction]
    category: Optional[list[str]] = None
    approval_state: PayoutApprovalState
    created_at: str


class GetPayoutListParams(PayOSBaseModel):
    reference_id: Optional[str] = None
    approval_state: Optional[PayoutApprovalState] = None
    category: Optional[str] = None
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


class PayoutListResponse(PayOSBaseModel):
    pagination: Pagination
    payouts: list[Payout]


class EstimateCredit(PayOSBaseModel):
    estimate_credit: int


__all__ = [
    "PayoutApprovalState",
    "PayoutTransactionState",
    "Payout",
    "PayoutListResponse",
    "PayoutRequest",
    "PayoutTransaction",
    "EstimateCredit",
    "GetPayoutListParams",
]
