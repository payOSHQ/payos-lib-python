from ...._core.models import PayOSBaseModel


class PayoutAccountInfo(PayOSBaseModel):
    account_number: str
    account_name: str
    currency: str
    balance: str


__all__ = [
    "PayoutAccountInfo",
]
