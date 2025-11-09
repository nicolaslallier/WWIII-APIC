"""Unit tests for register player use case edge cases."""

from unittest.mock import AsyncMock, patch

import pytest

from app.domain.player import Country, Player
from app.use_cases.register_player import RegisterPlayerUseCase


class TestRegisterPlayerUseCaseEdgeCases:
    """Test edge cases for RegisterPlayerUseCase."""

    @pytest.mark.asyncio
    async def test_register_player_bcrypt_fallback(self) -> None:
        """Test that bcrypt fallback is used when passlib fails."""
        # Given: a repository
        mock_repo = AsyncMock()
        mock_repo.find_by_username.return_value = None
        mock_repo.find_by_email.return_value = None

        created_player = None

        async def capture_create(player: Player) -> Player:
            nonlocal created_player
            created_player = player
            return player

        mock_repo.create.side_effect = capture_create

        use_case = RegisterPlayerUseCase(repository=mock_repo)

        # Mock passlib to raise ValueError with the specific message
        with patch.object(use_case._pwd_context, "hash") as mock_hash:
            mock_hash.side_effect = ValueError("password cannot be longer than 72 bytes")

            # When: registering a player (triggers fallback)
            await use_case.execute(
                username="player123",
                email="player@example.com",
                password="password123",
                country=Country.USA,
            )

            # Then: password is hashed using bcrypt fallback
            assert created_player is not None
            assert created_player.password_hash != "password123"
            assert len(created_player.password_hash) > 20  # bcrypt hash is long

    @pytest.mark.asyncio
    async def test_register_player_bcrypt_fallback_other_error(self) -> None:
        """Test that other ValueError is re-raised."""
        # Given: a repository
        mock_repo = AsyncMock()
        mock_repo.find_by_username.return_value = None
        mock_repo.find_by_email.return_value = None

        use_case = RegisterPlayerUseCase(repository=mock_repo)

        # Mock passlib to raise a different ValueError
        with patch.object(use_case._pwd_context, "hash") as mock_hash:
            mock_hash.side_effect = ValueError("Some other error")

            # When/Then: registering raises the error
            with pytest.raises(ValueError, match="Some other error"):
                await use_case.execute(
                    username="player123",
                    email="player@example.com",
                    password="password123",
                    country=Country.USA,
                )

