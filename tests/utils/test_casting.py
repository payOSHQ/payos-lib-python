"""Tests for casting utilities."""

from dataclasses import dataclass

import pytest
from pydantic import BaseModel

from payos.utils.casting import cast_to


# Test fixtures
class SampleModel(BaseModel):
    """Sample Pydantic model for testing."""

    name: str
    age: int


@dataclass
class SampleDataclass:
    """Sample dataclass for testing."""

    name: str
    age: int


class TestCastToBasicTypes:
    """Test cast_to with basic Python types."""

    def test_casts_to_str_from_int(self):
        """Test casting int to str."""
        result = cast_to(str, 123)
        assert result == "123"
        assert isinstance(result, str)

    def test_casts_to_str_from_float(self):
        """Test casting float to str."""
        result = cast_to(str, 3.14)
        assert result == "3.14"
        assert isinstance(result, str)

    def test_keeps_str_as_str(self):
        """Test that str stays as str."""
        result = cast_to(str, "hello")
        assert result == "hello"
        assert isinstance(result, str)

    def test_casts_to_int_from_str(self):
        """Test casting str to int."""
        result = cast_to(int, "123")
        assert result == 123
        assert isinstance(result, int)

    def test_casts_to_int_from_float(self):
        """Test casting float to int."""
        result = cast_to(int, 3.14)
        assert result == 3
        assert isinstance(result, int)

    def test_keeps_int_as_int(self):
        """Test that int stays as int."""
        result = cast_to(int, 42)
        assert result == 42
        assert isinstance(result, int)

    def test_casts_to_float_from_str(self):
        """Test casting str to float."""
        result = cast_to(float, "3.14")
        assert result == 3.14
        assert isinstance(result, float)

    def test_casts_to_float_from_int(self):
        """Test casting int to float."""
        result = cast_to(float, 42)
        assert result == 42.0
        assert isinstance(result, float)

    def test_keeps_float_as_float(self):
        """Test that float stays as float."""
        result = cast_to(float, 3.14)
        assert result == 3.14
        assert isinstance(result, float)

    def test_casts_to_bool_from_int(self):
        """Test casting int to bool."""
        result = cast_to(bool, 1)
        assert result is True
        assert isinstance(result, bool)

        result = cast_to(bool, 0)
        assert result is False

    def test_casts_to_bool_from_str(self):
        """Test casting str to bool."""
        # Any non-empty string is truthy
        result = cast_to(bool, "true")
        assert result is True

        result = cast_to(bool, "")
        assert result is False

    def test_keeps_bool_as_bool(self):
        """Test that bool stays as bool."""
        result = cast_to(bool, True)
        assert result is True
        assert isinstance(result, bool)

    def test_keeps_list_as_list(self):
        """Test that list stays as list."""
        data = [1, 2, 3]
        result = cast_to(list, data)
        assert result == [1, 2, 3]
        assert isinstance(result, list)

    def test_keeps_dict_as_dict(self):
        """Test that dict stays as dict."""
        data = {"a": 1, "b": 2}
        result = cast_to(dict, data)
        assert result == {"a": 1, "b": 2}
        assert isinstance(result, dict)

    def test_returns_none_when_data_is_none(self):
        """Test that None passes through for any type."""
        result = cast_to(str, None)
        assert result is None

        result = cast_to(int, None)
        assert result is None

    def test_raises_type_error_for_invalid_cast(self):
        """Test that invalid casts raise TypeError or ValueError."""
        with pytest.raises((TypeError, ValueError)):
            cast_to(int, "not-a-number")

        with pytest.raises((TypeError, ValueError)):
            cast_to(float, "not-a-float")


class TestCastToPydanticModels:
    """Test cast_to with Pydantic models."""

    def test_casts_dict_to_pydantic_model(self):
        """Test casting dict to Pydantic model."""
        data = {"name": "John", "age": 30}
        result = cast_to(SampleModel, data)

        assert isinstance(result, SampleModel)
        assert result.name == "John"
        assert result.age == 30

    def test_validates_pydantic_model_fields(self):
        """Test that Pydantic validation works during cast."""
        # Valid data
        data = {"name": "Jane", "age": 25}
        result = cast_to(SampleModel, data)
        assert result.name == "Jane"

        # Invalid data (missing required field)
        with pytest.raises((TypeError, ValueError)):
            cast_to(SampleModel, {"name": "Invalid"})

    def test_casts_pydantic_model_with_extra_fields(self):
        """Test casting dict with extra fields to Pydantic model."""
        data = {"name": "Bob", "age": 40, "extra": "ignored"}
        result = cast_to(SampleModel, data)

        assert result.name == "Bob"
        assert result.age == 40
        # Extra field should be ignored by default Pydantic config


class TestCastToDataclasses:
    """Test cast_to with dataclasses."""

    def test_casts_dict_to_dataclass(self):
        """Test casting dict to dataclass."""
        data = {"name": "Alice", "age": 28}
        result = cast_to(SampleDataclass, data)

        assert isinstance(result, SampleDataclass)
        assert result.name == "Alice"
        assert result.age == 28

    def test_raises_error_for_non_dict_to_dataclass(self):
        """Test that non-dict to dataclass raises TypeError."""
        with pytest.raises(TypeError, match="Cannot cast .* to dataclass"):
            cast_to(SampleDataclass, "not-a-dict")

    def test_raises_error_for_missing_dataclass_fields(self):
        """Test that missing required fields raise error."""
        with pytest.raises(TypeError):
            cast_to(SampleDataclass, {"name": "Incomplete"})


class TestCastToEdgeCases:
    """Test edge cases and fallback behavior."""

    def test_fallback_casting_for_custom_types(self):
        """Test fallback casting for types with constructors."""

        class CustomType:
            def __init__(self, value):
                self.value = value

        result = cast_to(CustomType, "test")
        assert isinstance(result, CustomType)
        assert result.value == "test"

    def test_raises_type_error_for_incompatible_types(self):
        """Test that incompatible types raise TypeError."""

        class NoConstructor:
            def __init__(self):
                raise ValueError("Cannot construct")

        with pytest.raises(TypeError, match="Cannot cast"):
            cast_to(NoConstructor, "data")

    def test_type_mismatch_for_basic_types(self):
        """Test that type mismatch raises TypeError for basic types."""
        with pytest.raises(TypeError, match="Cannot cast"):
            # Trying to cast list to dict should fail
            cast_to(dict, [1, 2, 3])

        with pytest.raises(TypeError, match="Cannot cast"):
            # Trying to cast dict to list should fail
            cast_to(list, {"a": 1})
