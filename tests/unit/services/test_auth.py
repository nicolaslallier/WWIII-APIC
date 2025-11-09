"""Unit tests for JWT auth service."""

from datetime import UTC, datetime, timedelta
from unittest.mock import Mock

import pytest
from jose import jwt

from app.core.config import Settings
from app.services.auth import AuthService


class TestAuthService:
    """Test AuthService."""

    def test_create_access_token(self) -> None:
        """Test creating an access token."""
        # Given: auth service with settings
        mock_settings = Mock(spec=Settings)
        mock_settings.jwt_secret_key = "test-secret-key"
        mock_settings.jwt_algorithm = "HS256"
        mock_settings.jwt_access_token_expire_minutes = 30

        auth_service = AuthService(settings=mock_settings)

        # When: creating an access token
        player_id = "123e4567-e89b-12d3-a456-426614174000"
        token = auth_service.create_access_token(player_id=player_id)

        # Then: token is created and can be decoded
        assert token is not None
        decoded = jwt.decode(
            token, mock_settings.jwt_secret_key, algorithms=[mock_settings.jwt_algorithm]
        )
        assert decoded["sub"] == player_id
        assert "exp" in decoded

    def test_create_access_token_with_expiration(self) -> None:
        """Test that token has correct expiration."""
        # Given: auth service with settings
        mock_settings = Mock(spec=Settings)
        mock_settings.jwt_secret_key = "test-secret-key"
        mock_settings.jwt_algorithm = "HS256"
        mock_settings.jwt_access_token_expire_minutes = 60

        auth_service = AuthService(settings=mock_settings)

        # When: creating an access token
        player_id = "123e4567-e89b-12d3-a456-426614174000"
        token = auth_service.create_access_token(player_id=player_id)

        # Then: token expiration is approximately correct
        decoded = jwt.decode(
            token, mock_settings.jwt_secret_key, algorithms=[mock_settings.jwt_algorithm]
        )
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=UTC)
        expected_exp = datetime.now(UTC) + timedelta(minutes=60)
        # Allow 5 second tolerance
        assert abs((exp_time - expected_exp).total_seconds()) < 5

    def test_verify_token_valid(self) -> None:
        """Test verifying a valid token."""
        # Given: auth service and a valid token
        mock_settings = Mock(spec=Settings)
        mock_settings.jwt_secret_key = "test-secret-key"
        mock_settings.jwt_algorithm = "HS256"
        mock_settings.jwt_access_token_expire_minutes = 30

        auth_service = AuthService(settings=mock_settings)
        player_id = "123e4567-e89b-12d3-a456-426614174000"
        token = auth_service.create_access_token(player_id=player_id)

        # When: verifying the token
        decoded = auth_service.verify_token(token)

        # Then: token is valid and contains correct player_id
        assert decoded is not None
        assert decoded["sub"] == player_id

    def test_verify_token_invalid(self) -> None:
        """Test verifying an invalid token."""
        # Given: auth service with different secret
        mock_settings = Mock(spec=Settings)
        mock_settings.jwt_secret_key = "test-secret-key"
        mock_settings.jwt_algorithm = "HS256"
        mock_settings.jwt_access_token_expire_minutes = 30

        auth_service = AuthService(settings=mock_settings)

        # When/Then: verifying invalid token raises exception
        from jose.exceptions import JWTError

        invalid_token = "invalid.token.here"
        with pytest.raises(JWTError):
            auth_service.verify_token(invalid_token)

    def test_verify_token_expired(self) -> None:
        """Test verifying an expired token."""
        # Given: auth service
        mock_settings = Mock(spec=Settings)
        mock_settings.jwt_secret_key = "test-secret-key"
        mock_settings.jwt_algorithm = "HS256"
        mock_settings.jwt_access_token_expire_minutes = -1  # Expired immediately

        auth_service = AuthService(settings=mock_settings)
        player_id = "123e4567-e89b-12d3-a456-426614174000"

        # Create token with negative expiration (expired)
        expired_token = jwt.encode(
            {"sub": player_id, "exp": datetime.now(UTC) - timedelta(minutes=1)},
            mock_settings.jwt_secret_key,
            algorithm=mock_settings.jwt_algorithm,
        )

        # When/Then: verifying expired token raises exception
        from jose.exceptions import ExpiredSignatureError

        with pytest.raises(ExpiredSignatureError):
            auth_service.verify_token(expired_token)

    def test_auth_service_missing_secret_key(self) -> None:
        """Test that missing JWT secret key raises ValueError."""
        # Given: settings without jwt_secret_key
        mock_settings = Mock(spec=Settings)
        mock_settings.jwt_secret_key = None

        # When/Then: creating AuthService raises ValueError
        with pytest.raises(ValueError, match="JWT_SECRET_KEY must be set"):
            AuthService(settings=mock_settings)

    def test_get_player_id_from_token_missing_sub(self) -> None:
        """Test that token without sub raises JWTError."""
        # Given: auth service
        mock_settings = Mock(spec=Settings)
        mock_settings.jwt_secret_key = "test-secret-key"
        mock_settings.jwt_algorithm = "HS256"
        mock_settings.jwt_access_token_expire_minutes = 30

        auth_service = AuthService(settings=mock_settings)

        # Create token without sub
        token_without_sub = jwt.encode(
            {"exp": datetime.now(UTC) + timedelta(minutes=30)},
            mock_settings.jwt_secret_key,
            algorithm=mock_settings.jwt_algorithm,
        )

        # When/Then: getting player ID raises JWTError
        from jose.exceptions import JWTError

        with pytest.raises(JWTError, match="Token does not contain player ID"):
            auth_service.get_player_id_from_token(token_without_sub)

    def test_get_player_id_from_token_invalid_sub_type(self) -> None:
        """Test that token with non-string sub raises JWTError."""
        # Given: auth service
        mock_settings = Mock(spec=Settings)
        mock_settings.jwt_secret_key = "test-secret-key"
        mock_settings.jwt_algorithm = "HS256"
        mock_settings.jwt_access_token_expire_minutes = 30

        auth_service = AuthService(settings=mock_settings)

        # Create token with non-string sub
        token_with_int_sub = jwt.encode(
            {"sub": 12345, "exp": datetime.now(UTC) + timedelta(minutes=30)},
            mock_settings.jwt_secret_key,
            algorithm=mock_settings.jwt_algorithm,
        )

        # When/Then: getting player ID raises JWTError
        from jose.exceptions import JWTError

        with pytest.raises(JWTError):
            auth_service.get_player_id_from_token(token_with_int_sub)

    def test_get_player_id_from_token_valid(self) -> None:
        """Test getting player ID from valid token."""
        # Given: auth service
        mock_settings = Mock(spec=Settings)
        mock_settings.jwt_secret_key = "test-secret-key"
        mock_settings.jwt_algorithm = "HS256"
        mock_settings.jwt_access_token_expire_minutes = 30

        auth_service = AuthService(settings=mock_settings)
        player_id = "123e4567-e89b-12d3-a456-426614174000"
        token = auth_service.create_access_token(player_id=player_id)

        # When: getting player ID from token
        extracted_id = auth_service.get_player_id_from_token(token)

        # Then: correct player ID is returned
        assert extracted_id == player_id
