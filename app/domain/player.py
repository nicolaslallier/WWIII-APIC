"""Player domain entity and value objects."""

import re
import uuid
from enum import Enum
from typing import Any, final


class Email:
    """Email value object."""

    def __init__(self, value: str) -> None:
        """
        Initialize Email value object.

        Args:
            value: Email string

        Raises:
            ValueError: If email is invalid or empty
        """
        if not value:
            raise ValueError("Email cannot be empty")

        # Simple email validation regex
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, value):
            raise ValueError("Invalid email format")

        self.value = value

    def __eq__(self, other: object) -> bool:
        """Compare Email objects."""
        if not isinstance(other, Email):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        """Hash Email object."""
        return hash(self.value)

    def __repr__(self) -> str:
        """String representation."""
        return f"Email('{self.value}')"


class Username:
    """Username value object."""

    def __init__(self, value: str) -> None:
        """
        Initialize Username value object.

        Args:
            value: Username string

        Raises:
            ValueError: If username is invalid
        """
        if not (3 <= len(value) <= 30):
            raise ValueError("Username must be between 3 and 30 characters")

        # Username can contain letters, numbers, underscores, and hyphens
        username_pattern = r"^[a-zA-Z0-9_-]+$"
        if not re.match(username_pattern, value):
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")

        self.value = value

    def __eq__(self, other: object) -> bool:
        """Compare Username objects."""
        if not isinstance(other, Username):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        """Hash Username object."""
        return hash(self.value)

    def __repr__(self) -> str:
        """String representation."""
        return f"Username('{self.value}')"


class Country(str, Enum):
    """Country/Faction enum for WWIII game."""

    USA = "USA"
    RUSSIA = "RUSSIA"
    CHINA = "CHINA"
    EUROPE = "EUROPE"


@final
class Player:
    """Player domain entity."""

    def __init__(
        self,
        username: Username,
        email: Email,
        password_hash: str,
        country: Country,
        initial_resources: dict[str, Any] | None = None,
        id: uuid.UUID | None = None,
    ) -> None:
        """
        Initialize Player entity.

        Args:
            username: Player username
            email: Player email
            password_hash: Hashed password
            country: Player country/faction
            initial_resources: Initial game resources
            id: Player ID (generated if not provided)
        """
        self.id = id or uuid.uuid4()
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.country = country
        self.initial_resources = initial_resources or {}

    def __eq__(self, other: object) -> bool:
        """Compare Player entities."""
        if not isinstance(other, Player):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash Player entity."""
        return hash(self.id)

    def __repr__(self) -> str:
        """String representation."""
        return f"Player(id={self.id}, username={self.username.value})"
