"""Legacy utils compatibility layer for v0.x API.

This module provides backward-compatible utility functions from payOS SDK v0.x.
All functions emit DeprecationWarning when used.

Migration guide:
    - convertObjToQueryStr() -> Use payos._crypto.CryptoProvider internally
    - sortObjDataByKey() -> Use payos._crypto.CryptoProvider internally
    - createSignatureFromObj() -> Use payos._crypto.CryptoProvider.create_signature_from_object()
    - createSignatureOfPaymentRequest() -> Use payos._crypto.CryptoProvider.create_signature_of_payment_request()
"""

import hashlib
import hmac
import json
import warnings
from typing import Any


def _sort_obj_data_by_key(obj: dict[str, Any]) -> dict[str, Any]:
    """Internal: Sort dictionary by keys (no deprecation warning)."""
    return dict(sorted(obj.items()))


def _convert_obj_to_query_str(obj: dict[str, Any]) -> str:
    """Internal: Convert dictionary to URL query string format (no deprecation warning)."""
    query_string = []

    for key, value in obj.items():
        value_as_string = ""
        if isinstance(value, (int, float, bool)):
            value_as_string = str(value)
        elif value in [None, "null", "NULL"]:
            value_as_string = ""
        elif isinstance(value, list):
            value_as_string = json.dumps(
                [dict(sorted(item.items())) for item in value], separators=(",", ":")
            ).replace("None", "null")
        else:
            value_as_string = str(value)
        query_string.append(f"{key}={value_as_string}")

    return "&".join(query_string)


def _create_signature_from_obj(data: dict[str, Any], key: str) -> str:
    """Internal: Create HMAC-SHA256 signature from dictionary (no deprecation warning)."""
    sorted_data_by_key = _sort_obj_data_by_key(data)
    data_query_str = _convert_obj_to_query_str(sorted_data_by_key)
    return hmac.new(
        key.encode("utf-8"), msg=data_query_str.encode("utf-8"), digestmod=hashlib.sha256
    ).hexdigest()


def _create_signature_of_payment_request(data: Any, key: str) -> str:
    """Internal: Create signature for payment request (no deprecation warning)."""
    if hasattr(data, "amount"):
        amount = data.amount
    else:
        amount = data.get("amount", "")

    if hasattr(data, "cancelUrl"):
        cancel_url = data.cancelUrl
    elif hasattr(data, "cancel_url"):
        cancel_url = data.cancel_url
    else:
        cancel_url = data.get("cancelUrl", data.get("cancel_url", ""))

    if hasattr(data, "description"):
        description = data.description
    else:
        description = data.get("description", "")

    if hasattr(data, "orderCode"):
        order_code = data.orderCode
    elif hasattr(data, "order_code"):
        order_code = data.order_code
    else:
        order_code = data.get("orderCode", data.get("order_code", ""))

    if hasattr(data, "returnUrl"):
        return_url = data.returnUrl
    elif hasattr(data, "return_url"):
        return_url = data.return_url
    else:
        return_url = data.get("returnUrl", data.get("return_url", ""))

    data_str = f"amount={amount}&cancelUrl={cancel_url}&description={description}&orderCode={order_code}&returnUrl={return_url}"
    return hmac.new(
        key.encode("utf-8"), msg=data_str.encode("utf-8"), digestmod=hashlib.sha256
    ).hexdigest()


def sortObjDataByKey(obj: dict[str, Any]) -> dict[str, Any]:
    """Sort dictionary by keys.

    .. deprecated:: 1.0.0
        This is an internal utility. Use the SDK's built-in signature methods instead.
    """
    warnings.warn(
        "sortObjDataByKey() is deprecated and will be removed in v2.0.0. "
        "Use the SDK's built-in signature methods instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _sort_obj_data_by_key(obj)


def convertObjToQueryStr(obj: dict[str, Any]) -> str:
    """Convert dictionary to URL query string format.

    .. deprecated:: 1.0.0
        This is an internal utility. Use the SDK's built-in signature methods instead.
    """
    warnings.warn(
        "convertObjToQueryStr() is deprecated and will be removed in v2.0.0. "
        "Use the SDK's built-in signature methods instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _convert_obj_to_query_str(obj)


def createSignatureFromObj(data: dict[str, Any], key: str) -> str:
    """Create HMAC-SHA256 signature from dictionary.

    .. deprecated:: 1.0.0
        Use payos._crypto.CryptoProvider.create_signature_from_object() instead.
    """
    warnings.warn(
        "createSignatureFromObj() is deprecated and will be removed in v2.0.0. "
        "Use payos._crypto.CryptoProvider.create_signature_from_object() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _create_signature_from_obj(data, key)


def createSignatureOfPaymentRequest(data: Any, key: str) -> str:
    """Create signature for payment request.

    .. deprecated:: 1.0.0
        Use payos._crypto.CryptoProvider.create_signature_of_payment_request() instead.
    """
    warnings.warn(
        "createSignatureOfPaymentRequest() is deprecated and will be removed in v2.0.0. "
        "Use payos._crypto.CryptoProvider.create_signature_of_payment_request() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _create_signature_of_payment_request(data, key)
