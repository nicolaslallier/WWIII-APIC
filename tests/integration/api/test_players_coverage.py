"""Integration tests for API endpoint to ensure full coverage."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.api.v1.players import register_player
from app.domain.player import Country, Email, Player, Username
from app.schemas.player import PlayerRegisterRequest
from app.use_cases.register_player import DuplicatePlayerError


@pytest.mark.asyncio
async def test_register_player_endpoint_success_path() -> None:
    """Test successful registration path covers all lines 105-120."""
    # Create a real player entity
    player = Player(
        id=uuid4(),
        username=Username("testuser"),
        email=Email("test@example.com"),
        password_hash="hashed",
        country=Country.USA,
    )

    # Mock dependencies
    mock_use_case = AsyncMock()
    mock_use_case.execute = AsyncMock(return_value=player)

    mock_auth_service = MagicMock()
    mock_auth_service.create_access_token = MagicMock(return_value="test-token")

    mock_session = AsyncMock()
    mock_db_player = MagicMock()
    mock_db_player.created_at = datetime.now()
    mock_result = MagicMock()
    mock_result.scalar_one = MagicMock(return_value=mock_db_player)
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Create request
    request = PlayerRegisterRequest(
        username="testuser",
        email="test@example.com",
        password="password123",
        country=Country.USA,
    )

    # Call the endpoint function directly
    response = await register_player(
        request=request,
        use_case=mock_use_case,
        auth_service=mock_auth_service,
        session=mock_session,
    )

    # Verify response
    assert response.player.username == "testuser"
    assert response.access_token == "test-token"
    # This covers lines 105-120


@pytest.mark.asyncio
async def test_register_player_endpoint_duplicate_error() -> None:
    """Test duplicate error handler covers lines 132-133."""
    mock_use_case = AsyncMock()
    mock_use_case.execute = AsyncMock(side_effect=DuplicatePlayerError("Duplicate"))

    request = PlayerRegisterRequest(
        username="testuser",
        email="test@example.com",
        password="password123",
        country=Country.USA,
    )

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        await register_player(
            request=request,
            use_case=mock_use_case,
            auth_service=MagicMock(),
            session=AsyncMock(),
        )

    assert exc_info.value.status_code == 409
    # This covers lines 132-133


@pytest.mark.asyncio
async def test_register_player_endpoint_value_error() -> None:
    """Test ValueError handler covers lines 138-139."""
    mock_use_case = AsyncMock()
    mock_use_case.execute = AsyncMock(side_effect=ValueError("Validation error"))

    request = PlayerRegisterRequest(
        username="testuser",
        email="test@example.com",
        password="password123",
        country=Country.USA,
    )

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        await register_player(
            request=request,
            use_case=mock_use_case,
            auth_service=MagicMock(),
            session=AsyncMock(),
        )

    assert exc_info.value.status_code == 422
    # This covers lines 138-139

