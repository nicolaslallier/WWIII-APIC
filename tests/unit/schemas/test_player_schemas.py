"""Unit tests for player schemas."""

import pytest
from pydantic import ValidationError

from app.domain.player import Country
from app.schemas.player import PlayerRegisterRequest


class TestPlayerSchemas:
    """Test player Pydantic schemas."""

    def test_username_validator_invalid_characters(self) -> None:
        """Test username validator with invalid characters."""
        # Given: invalid username with special characters
        invalid_data = {
            "username": "user@name",  # Contains @
            "email": "user@example.com",
            "password": "password123",
            "country": Country.USA,
        }

        # When/Then: validation raises ValueError
        with pytest.raises(ValidationError) as exc_info:
            PlayerRegisterRequest(**invalid_data)

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("username",) and "can only contain" in str(error["msg"]).lower()
            for error in errors
        )

