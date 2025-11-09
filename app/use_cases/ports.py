"""Use case ports (Protocols) for dependency injection."""

from typing import Protocol

from app.domain.player import Player


class PlayerRepository(Protocol):
    """Protocol for player repository."""

    async def find_by_username(self, username: str) -> Player | None:
        """
        Find player by username.

        Args:
            username: Username to search for

        Returns:
            Player if found, None otherwise
        """
        ...

    async def find_by_email(self, email: str) -> Player | None:
        """
        Find player by email.

        Args:
            email: Email to search for

        Returns:
            Player if found, None otherwise
        """
        ...

    async def create(self, player: Player) -> Player:
        """
        Create a new player.

        Args:
            player: Player entity to create

        Returns:
            Created player entity
        """
        ...
