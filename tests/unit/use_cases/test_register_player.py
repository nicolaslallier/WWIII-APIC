"""Unit tests for RegisterPlayerUseCase."""

from unittest.mock import AsyncMock

import pytest

from app.domain.player import Country, Email, Player, Username
from app.use_cases.register_player import DuplicatePlayerError, RegisterPlayerUseCase


class TestRegisterPlayerUseCase:
    """Test RegisterPlayerUseCase."""

    @pytest.mark.asyncio
    async def test_register_player_success(self) -> None:
        """Test successful player registration."""
        # Given: a player repository and use case
        mock_repo = AsyncMock()
        mock_repo.find_by_username.return_value = None
        mock_repo.find_by_email.return_value = None
        mock_repo.create.return_value = Player(
            username=Username("player123"),
            email=Email("player@example.com"),
            password_hash="hashed_password",
            country=Country.USA,
            initial_resources={"money": 1000},
        )

        use_case = RegisterPlayerUseCase(repository=mock_repo)

        # When: registering a new player
        result = await use_case.execute(
            username="player123",
            email="player@example.com",
            password="password123",
            country=Country.USA,
            initial_resources={"money": 1000},
        )

        # Then: player is created successfully
        assert result is not None
        assert result.username.value == "player123"
        assert result.email.value == "player@example.com"
        assert result.country == Country.USA
        mock_repo.find_by_username.assert_awaited_once_with("player123")
        mock_repo.find_by_email.assert_awaited_once_with("player@example.com")
        mock_repo.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_register_player_duplicate_username(self) -> None:
        """Test registration fails when username already exists."""
        # Given: a player repository with existing username
        mock_repo = AsyncMock()
        mock_repo.find_by_username.return_value = Player(
            username=Username("player123"),
            email=Email("existing@example.com"),
            password_hash="hash",
            country=Country.USA,
        )
        mock_repo.find_by_email.return_value = None

        use_case = RegisterPlayerUseCase(repository=mock_repo)

        # When/Then: registering with duplicate username raises error
        with pytest.raises(DuplicatePlayerError, match="Username already exists"):
            await use_case.execute(
                username="player123",
                email="player@example.com",
                password="password123",
                country=Country.USA,
            )

        mock_repo.find_by_username.assert_awaited_once_with("player123")
        mock_repo.find_by_email.assert_not_awaited()
        mock_repo.create.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_register_player_duplicate_email(self) -> None:
        """Test registration fails when email already exists."""
        # Given: a player repository with existing email
        mock_repo = AsyncMock()
        mock_repo.find_by_username.return_value = None
        mock_repo.find_by_email.return_value = Player(
            username=Username("otherplayer"),
            email=Email("player@example.com"),
            password_hash="hash",
            country=Country.RUSSIA,
        )

        use_case = RegisterPlayerUseCase(repository=mock_repo)

        # When/Then: registering with duplicate email raises error
        with pytest.raises(DuplicatePlayerError, match="Email already exists"):
            await use_case.execute(
                username="player123",
                email="player@example.com",
                password="password123",
                country=Country.USA,
            )

        mock_repo.find_by_username.assert_awaited_once_with("player123")
        mock_repo.find_by_email.assert_awaited_once_with("player@example.com")
        mock_repo.create.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_register_player_hashes_password(self) -> None:
        """Test that password is hashed before storing."""
        # Given: a player repository
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

        # When: registering a player
        await use_case.execute(
            username="player123",
            email="player@example.com",
            password="password123",
            country=Country.USA,
        )

        # Then: password is hashed (not plain text)
        assert created_player is not None
        assert created_player.password_hash != "password123"
        assert len(created_player.password_hash) > 20  # bcrypt hash is long
