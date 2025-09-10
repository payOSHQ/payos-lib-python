"""Base Pydantic models for payOS SDK."""

from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class PayOSBaseModel(BaseModel):
    """Base Pydantic model with camelCase field aliases."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,  # Allow both snake_case and camelCase field names
        extra="forbid",  # Forbid extra fields
    )

    def model_dump_camel_case(self, **kwargs: Any) -> dict[str, Any]:
        """Export model with camelCase field names."""
        return self.model_dump(by_alias=True, **kwargs)

    def model_dump_snake_case(self, **kwargs: Any) -> dict[str, Any]:
        """Export model with snake_case field names."""
        return self.model_dump(by_alias=False, **kwargs)

    def to_json(self, **kwargs: Any) -> str:
        """Convert model to json."""
        return self.model_dump_json(**kwargs)
