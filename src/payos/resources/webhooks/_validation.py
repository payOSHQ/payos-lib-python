"""Webhook data validation helpers."""

import json
from typing import Any

from ..._core.exceptions import WebhookError

MAX_SAFE = 2**53 - 1

CORE_INT = ("orderCode", "amount")
CORE_STR = (
    "description",
    "accountNumber",
    "reference",
    "transactionDateTime",
    "currency",
    "paymentLinkId",
    "code",
    "desc",
)
OPTIONAL_STR = (
    "counterAccountBankId",
    "counterAccountBankName",
    "counterAccountName",
    "counterAccountNumber",
    "virtualAccountName",
    "virtualAccountNumber",
)

_KEY_CHARS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")


def _invalid(reason: str) -> WebhookError:
    return WebhookError(f"Invalid webhook data: {reason}")


def _is_valid_key(k: object) -> bool:
    return (
        isinstance(k, str) and k != "__proto__" and len(k) > 0 and all(ch in _KEY_CHARS for ch in k)
    )


def _is_safe_int(v: object) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and -MAX_SAFE <= v <= MAX_SAFE


def validate_webhook_data(data: object) -> dict:
    if not isinstance(data, dict):
        raise _invalid("data must be an object")

    for key, value in data.items():
        if not _is_valid_key(key):
            raise _invalid(f"invalid key {key!r}")
        if value is None or _is_safe_int(value):
            continue
        if isinstance(value, str):
            if "=" in value:
                raise _invalid(f"value of {key} contains '='")
            continue
        raise _invalid(f"invalid value type for {key}")

    for key in CORE_INT:
        if key not in data or not _is_safe_int(data[key]):
            raise _invalid(f"{key} must be an integer")
    for key in CORE_STR:
        if key not in data or not isinstance(data[key], str):
            raise _invalid(f"{key} must be a string")
    for key in OPTIONAL_STR:
        if key in data and data[key] is not None and not isinstance(data[key], str):
            raise _invalid(f"{key} must be a string or null")

    return data


def load_json_no_duplicates(text: str) -> object:
    def hook(pairs: list[tuple[str, Any]]) -> dict:
        result: dict = {}
        for key, value in pairs:
            if key in result:
                raise WebhookError(f"Invalid webhook data: duplicate key {key!r}")
            result[key] = value
        return result

    try:
        return json.loads(text, object_pairs_hook=hook)
    except json.JSONDecodeError as e:
        raise WebhookError("Invalid JSON") from e


def validate_model_values(data_dict: dict) -> None:
    for key, value in data_dict.items():
        if isinstance(value, str) and "=" in value:
            raise _invalid(f"value of {key} contains '='")
    for key in CORE_INT:
        if not _is_safe_int(data_dict.get(key)):
            raise _invalid(f"{key} must be an integer")
