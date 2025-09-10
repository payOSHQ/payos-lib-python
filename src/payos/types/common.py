"""Common type definitions across all payOS API versions."""

from typing import Optional

from .._core.models import PayOSBaseModel


class PayOSResponse(PayOSBaseModel):
    code: str
    desc: str
    data: Optional[dict] = None
    signature: Optional[str] = None
