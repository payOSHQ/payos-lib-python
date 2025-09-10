from typing import Any


def validate_positive_number(name: str, value: Any) -> None:
    """Validate that a value is a positive number."""
    if not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"{name} must be a positive number")
