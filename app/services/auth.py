"""JWT authentication service."""

from datetime import UTC, datetime, timedelta

from jose import jwt
from jose.exceptions import JWTError

from app.core.config import Settings


class AuthService:
    """Service for JWT token generation and verification."""

    def __init__(self, settings: Settings) -> None:
        """
        Initialize AuthService.

        Args:
            settings: Application settings
        """
        self._settings = settings
        if not settings.jwt_secret_key:
            raise ValueError("JWT_SECRET_KEY must be set")
        # After validation, jwt_secret_key is guaranteed to be str
        self._jwt_secret_key: str = settings.jwt_secret_key

    def create_access_token(self, player_id: str) -> str:
        """
        Create a JWT access token.

        Args:
            player_id: Player ID to encode in token

        Returns:
            JWT access token string
        """
        expire = datetime.now(UTC) + timedelta(
            minutes=self._settings.jwt_access_token_expire_minutes
        )
        to_encode = {"sub": player_id, "exp": expire}
        encoded_jwt: str = jwt.encode(
            to_encode,
            self._jwt_secret_key,
            algorithm=self._settings.jwt_algorithm,
        )
        return encoded_jwt

    def verify_token(self, token: str) -> dict[str, str | int]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded token payload

        Raises:
            ExpiredSignatureError: If token is expired
            JWTError: If token is invalid
        """
        payload: dict[str, str | int] = jwt.decode(
            token,
            self._jwt_secret_key,
            algorithms=[self._settings.jwt_algorithm],
        )
        return payload

    def get_player_id_from_token(self, token: str) -> str:
        """
        Extract player ID from JWT token.

        Args:
            token: JWT token string

        Returns:
            Player ID from token

        Raises:
            ExpiredSignatureError: If token is expired
            JWTError: If token is invalid
        """
        payload = self.verify_token(token)
        sub_value = payload.get("sub")
        if not sub_value or not isinstance(sub_value, str):
            raise JWTError("Token does not contain player ID")
        return sub_value
