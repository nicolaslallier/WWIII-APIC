"""Unit tests for register player use case - bcrypt fallback edge case."""

from unittest.mock import AsyncMock, patch

import pytest

from app.domain.player import Country
from app.use_cases.register_player import RegisterPlayerUseCase


class TestRegisterPlayerUseCaseBcryptFallback:
    """Test bcrypt fallback edge case."""

    @pytest.mark.asyncio
    async def test_register_player_bcrypt_fallback_password_truncation(self) -> None:
        """Test that password > 72 bytes is truncated in bcrypt fallback."""
        # Given: a repository
        mock_repo = AsyncMock()
        mock_repo.find_by_username.return_value = None
        mock_repo.find_by_email.return_value = None

        created_player = None

        async def capture_create(player) -> None:
            nonlocal created_player
            created_player = player

        mock_repo.create.side_effect = capture_create

        use_case = RegisterPlayerUseCase(repository=mock_repo)

        # Mock passlib to raise ValueError with the specific message
        with patch.object(use_case._pwd_context, "hash") as mock_hash:
            mock_hash.side_effect = ValueError("password cannot be longer than 72 bytes")

            # When: registering with a password > 72 bytes (triggers fallback and truncation)
            long_password = "a" * 100  # 100 bytes
            await use_case.execute(
                username="player123",
                email="player@example.com",
                password=long_password,
                country=Country.USA,
            )

            # Then: password is hashed using bcrypt fallback (truncated to 72 bytes)
            assert created_player is not None
            assert created_player.password_hash != long_password
            assert len(created_player.password_hash) > 20  # bcrypt hash is long

