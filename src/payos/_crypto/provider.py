"""Crypto utilities for payOS SDK."""

import hashlib
import hmac
import json
import uuid
from typing import Any, Optional, Union
from urllib.parse import quote

from .._core.models import PayOSBaseModel


def _convert_value_to_string(value: Any) -> str:
    """Convert a value to string with proper JSON boolean handling."""
    if isinstance(value, bool):
        return "true" if value else "false"
    elif value is None:
        return ""
    else:
        return str(value)


def _convert_to_camel_case_dict(obj: Any) -> dict[str, Any]:
    """Convert a Pydantic model or dict to camelCase dict."""
    if isinstance(obj, PayOSBaseModel):
        # Use the model's camelCase dump method if available
        if hasattr(obj, "model_dump_camel_case"):
            return obj.model_dump_camel_case()
        else:
            # Fallback to by_alias=True for standard Pydantic models
            return obj.model_dump(by_alias=True)
    elif isinstance(obj, dict):
        return obj
    else:
        raise ValueError(f"Unsupported object type for signature generation: {type(obj)}")


def sort_object_by_key(obj: dict[str, Any]) -> dict[str, Any]:
    """Sort object keys in ascending order."""
    return {key: obj[key] for key in sorted(obj.keys())}


def deep_sort_object(obj: Any, sort_arrays: bool = False) -> Any:
    """Deep sort object with optional array sorting."""
    if isinstance(obj, dict):
        sorted_obj = {}
        for key in sorted(obj.keys()):
            value = obj[key]
            sorted_obj[key] = deep_sort_object(value, sort_arrays)
        return sorted_obj
    elif isinstance(obj, list):
        if sort_arrays:
            # Sort array elements
            sorted_items = []
            for item in obj:
                processed_item = (
                    deep_sort_object(item, sort_arrays) if isinstance(item, (dict, list)) else item
                )
                sorted_items.append(processed_item)

            # Sort by string representation
            sorted_items.sort(
                key=lambda x: (
                    json.dumps(x, sort_keys=True, ensure_ascii=False)
                    if isinstance(x, (dict, list))
                    else str(x)
                )
            )
            return sorted_items
        else:
            # Maintain array order, but sort objects within arrays
            return [
                deep_sort_object(item, sort_arrays) if isinstance(item, (dict, list)) else item
                for item in obj
            ]
    else:
        return obj


def convert_object_to_query_string(obj: dict[str, Any]) -> str:
    """Convert object to query string format."""
    parts = []

    for key in sorted(obj.keys()):
        value = obj[key]

        # Skip undefined values
        if value is None:
            value = ""
        elif isinstance(value, list):
            # Sort nested objects in arrays and stringify
            sorted_list = [
                sort_object_by_key(item) if isinstance(item, dict) else item for item in value
            ]
            value = json.dumps(sorted_list, separators=(",", ":"), ensure_ascii=False)
        elif value in [None, "undefined", "null"]:
            value = ""
        else:
            value = _convert_value_to_string(value)

        parts.append(f"{key}={value}")

    return "&".join(parts)


class CryptoProvider:
    """Crypto provider for signature generation and validation."""

    def create_signature_from_object(
        self, data: Union[dict[str, Any], Any], key: str
    ) -> Optional[str]:
        """Create HMAC signature from object data."""
        if data is None or not key:
            return None

        # Convert Pydantic models to camelCase dict
        if not isinstance(data, dict):
            data = _convert_to_camel_case_dict(data)

        sorted_data = sort_object_by_key(data)
        query_string = convert_object_to_query_string(sorted_data)

        return hmac.new(
            key.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256
        ).hexdigest()

    def create_signature_of_payment_request(
        self, data: Union[dict[str, Any], Any], key: str
    ) -> Optional[str]:
        """Create signature for payment request using specific fields."""
        if data is None or not key:
            return None

        data = _convert_to_camel_case_dict(data)

        # Extract specific fields for payment request signature
        required_fields = ["amount", "cancelUrl", "description", "orderCode", "returnUrl"]
        values = []

        for field in required_fields:
            if field not in data:
                return None
            values.append(f"{field}={_convert_value_to_string(data[field])}")

        data_string = "&".join(values)

        return hmac.new(
            key.encode("utf-8"), data_string.encode("utf-8"), hashlib.sha256
        ).hexdigest()

    def create_signature(
        self,
        secret_key: str,
        json_data: Union[dict[str, Any], Any],
        *,
        encode_uri: bool = True,
        sort_arrays: bool = False,
        algorithm: str = "sha256",
    ) -> str:
        """Create HMAC signature from JSON data with query string format."""
        # Convert Pydantic models to camelCase dict
        if not isinstance(json_data, dict):
            json_data = _convert_to_camel_case_dict(json_data)

        sorted_data = deep_sort_object(json_data, sort_arrays)

        query_parts = []
        for key in sorted(sorted_data.keys()):
            value = sorted_data[key]

            # Handle different value types
            if isinstance(value, list):
                value = json.dumps(value, separators=(",", ":"), ensure_ascii=False)
            elif isinstance(value, dict):
                value = json.dumps(value, separators=(",", ":"), ensure_ascii=False)
            elif value is None:
                value = ""
            else:
                value = _convert_value_to_string(value)

            # Conditionally URL encode based on options
            if encode_uri:
                encoded_key = quote(str(key))
                encoded_value = quote(value)
                query_parts.append(f"{encoded_key}={encoded_value}")
            else:
                query_parts.append(f"{key}={value}")

        query_string = "&".join(query_parts)

        # Create HMAC signature
        if algorithm == "sha256":
            hash_func = hashlib.sha256
        elif algorithm == "sha1":
            hash_func = hashlib.sha1
        elif algorithm == "sha512":
            hash_func = hashlib.sha512
        elif algorithm == "md5":
            hash_func = hashlib.md5
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        return hmac.new(
            secret_key.encode("utf-8"), query_string.encode("utf-8"), hash_func
        ).hexdigest()

    def create_uuid4(self) -> str:
        """Generate a random UUID4 string."""
        return str(uuid.uuid4())
