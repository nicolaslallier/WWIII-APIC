"""Pydantic schemas for player API."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.domain.player import Country


class PlayerRegisterRequest(BaseModel):
    """Request schema for player registration."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        description="Player username",
        examples=["player123"],
    )
    email: EmailStr = Field(
        ...,
        description="Player email address",
        examples=["player@example.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Player password (minimum 8 characters)",
        examples=["securepassword123"],
    )
    country: Country = Field(
        ...,
        description="Player country/faction",
        examples=[Country.USA],
    )
    initial_resources: dict[str, Any] = Field(
        default_factory=dict,
        description="Initial game resources",
        examples=[{"money": 1000, "troops": 100}],
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        import re

        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
        return v

    model_config = {"extra": "forbid"}


class PlayerResponse(BaseModel):
    """Response schema for player data."""

    id: UUID = Field(..., description="Player ID")
    username: str = Field(..., description="Player username")
    email: EmailStr = Field(..., description="Player email")
    country: Country = Field(..., description="Player country/faction")
    created_at: datetime = Field(..., description="Account creation timestamp")

    model_config = {"extra": "forbid"}


class PlayerRegisterResponse(BaseModel):
    """Response schema for player registration."""

    player: PlayerResponse = Field(..., description="Registered player data")
    access_token: str = Field(..., description="JWT access token")

    model_config = {"extra": "forbid"}
