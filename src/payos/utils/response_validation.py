"""Shape validation for body-signed API response data, applied before the signature is computed.

The body signature is computed over ``key=value`` pairs joined by ``&`` without any encoding,
with lists serialised as JSON. The received data must therefore not be able to shift delimiters,
replace a scalar with an object or turn a list into a string that swallows the remaining fields.
"""

import re
import math
from typing import Any

from .._core.exceptions import InvalidSignatureError

_KEY_PATTERN = re.compile(r"^[A-Za-z0-9_]+$")
# A ``&key=`` sequence inside a value is what lets the unencoded signed string be re-split.
_SMUGGLING_PATTERN = re.compile(r"&[A-Za-z0-9_]+=")
_MAX_SAFE_INTEGER = 2**53 - 1


def _invalid(reason: str) -> InvalidSignatureError:
    return InvalidSignatureError(f"Invalid response data: {reason}")


def _validate_scalar(path: str, value: Any) -> None:
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int):
        if abs(value) > _MAX_SAFE_INTEGER:
            raise _invalid(f'"{path}" must be a safe integer')
    elif isinstance(value, float):
        if not math.isfinite(value) or (value.is_integer() and abs(value) > _MAX_SAFE_INTEGER):
            raise _invalid(f'"{path}" must be a finite number within the safe integer range')
    elif isinstance(value, str):
        if _SMUGGLING_PATTERN.search(value):
            raise _invalid(f'"{path}" must not contain a "&key=" sequence')
    else:
        raise _invalid(f'"{path}" has an unsupported type')


def _validate_keys(path: str, record: dict[Any, Any]) -> None:
    for key in record:
        if not isinstance(key, str) or not _KEY_PATTERN.match(key) or key == "__proto__":
            raise _invalid(f'unsupported key "{path}{key}"')


def validate_response_data(data: Any) -> None:
    """Validate the ``data`` object of a response signed with the ``body`` signature.

    Top-level values may be scalars (string without a ``&key=`` sequence, finite number, bool, null) or lists of
    objects/scalars. Nested objects are only accepted inside lists and may only contain scalars.

    Raises:
        InvalidSignatureError: when the data does not have the expected shape.
    """
    if not isinstance(data, dict):
        raise _invalid("data must be a JSON object")

    _validate_keys("", data)
    for key, value in data.items():
        if not isinstance(value, list):
            _validate_scalar(key, value)
            continue
        for index, item in enumerate(value):
            path = f"{key}[{index}]"
            if isinstance(item, dict):
                _validate_keys(f"{path}.", item)
                for field, field_value in item.items():
                    _validate_scalar(f"{path}.{field}", field_value)
            else:
                _validate_scalar(path, item)
