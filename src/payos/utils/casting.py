from typing import Any, TypeVar, cast

T = TypeVar("T")


def cast_to(cast_to_type: type[T], data: Any) -> T:
    """Cast data to the specified type."""
    if data is None:
        return cast(T, data)

    # Handle basic types
    if cast_to_type in (str, int, float, bool, list, dict):
        if cast_to_type is str and not isinstance(data, str):
            return cast(T, str(data))
        elif cast_to_type is int and not isinstance(data, int):
            return cast(T, int(data))
        elif cast_to_type is float and not isinstance(data, float):
            return cast(T, float(data))
        elif cast_to_type is bool and not isinstance(data, bool):
            return cast(T, bool(data))
        elif isinstance(data, cast_to_type):
            return cast(T, data)  # type: ignore[redundant-cast]
        else:
            raise TypeError(f"Cannot cast {type(data)} to {cast_to_type}")

    # Handle Pydantic models
    try:
        if hasattr(cast_to_type, "model_validate"):
            # Pydantic v2
            return cast_to_type.model_validate(data)  # type: ignore
    except ImportError:
        pass

    # Handle dataclasses
    try:
        import dataclasses

        if dataclasses.is_dataclass(cast_to_type):
            if isinstance(data, dict):
                return cast_to_type(**data)
            else:
                raise TypeError(f"Cannot cast {type(data)} to dataclass {cast_to_type}")
    except ImportError:
        pass

    # Fallback: try direct casting
    try:
        return cast_to_type(data)  # type: ignore
    except Exception as e:
        raise TypeError(f"Cannot cast {type(data)} to {cast_to_type}: {e}") from e
