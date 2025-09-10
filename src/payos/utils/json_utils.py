import json
from typing import Any, Optional, cast

from httpx import Request, Response


def safe_json_parse(text: str) -> Optional[dict[str, Any]]:
    """Safely parse JSON text, returning None if invalid."""
    try:
        raw = json.loads(text)
        return cast(dict[str, Any], raw)
    except (json.JSONDecodeError, ValueError):
        return None


def build_query_string(params: dict[str, Any]) -> str:
    """Build query string from parameters."""
    from urllib.parse import urlencode

    # Filter out None values and convert to strings
    filtered_params = {}
    for key, value in params.items():
        if value is not None:
            if isinstance(value, (dict, list)):
                filtered_params[key] = json.dumps(value)
            else:
                filtered_params[key] = str(value)

    return urlencode(filtered_params)


def request_to_dict(request: Request) -> dict[str, Any]:
    data: dict[str, Any] = {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
    }
    try:
        data["json"] = json.loads(request.content) if request.content else None
    except (json.JSONDecodeError, UnicodeDecodeError):
        data["body"] = request.content.decode(errors="replace") if request.content else None
    return data


def response_to_dict(response: Response) -> dict[str, Any]:
    data: dict[str, Any] = {
        "status_code": response.status_code,
        "reason_phrase": response.reason_phrase,
        "http_version": response.http_version,
        "url": str(response.url),
        "headers": dict(response.headers),
    }
    try:
        data["body"] = response.json()
    except (json.JSONDecodeError, ValueError):
        data["body"] = response.text
    return data
