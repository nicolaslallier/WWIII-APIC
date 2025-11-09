"""Register player use case."""

from passlib.context import CryptContext

from app.domain.player import Country, Email, Player, Username
from app.use_cases.ports import PlayerRepository


class DuplicatePlayerError(Exception):
    """Raised when attempting to register a duplicate player."""

    pass


class RegisterPlayerUseCase:
    """Use case for registering a new player."""

    def __init__(self, repository: PlayerRepository) -> None:
        """
        Initialize RegisterPlayerUseCase.

        Args:
            repository: Player repository implementation
        """
        self._repository = repository
        # Initialize password context with explicit bcrypt configuration
        # to avoid wrap bug detection issues during initialization
        self._pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__ident="2b",  # Use bcrypt 2b format explicitly
        )

    async def execute(
        self,
        username: str,
        email: str,
        password: str,
        country: Country,
        initial_resources: dict[str, int] | None = None,
    ) -> Player:
        """
        Register a new player.

        Args:
            username: Player username
            email: Player email
            password: Plain text password
            country: Player country/faction
            initial_resources: Initial game resources

        Returns:
            Created player entity

        Raises:
            DuplicatePlayerError: If username or email already exists
        """
        # Check for duplicate username
        existing_player = await self._repository.find_by_username(username)
        if existing_player is not None:
            raise DuplicatePlayerError("Username already exists")

        # Check for duplicate email
        existing_player = await self._repository.find_by_email(email)
        if existing_player is not None:
            raise DuplicatePlayerError("Email already exists")

        # Hash password
        # Note: passlib may trigger bcrypt wrap bug detection on first hash call
        # which can fail with test passwords > 72 bytes. Handle this gracefully.
        try:
            password_hash = self._pwd_context.hash(password)
        except ValueError as e:
            if "password cannot be longer than 72 bytes" in str(e):
                # This is passlib's internal wrap bug detection failing
                # Fall back to using bcrypt directly
                import bcrypt

                password_bytes = password.encode("utf-8")
                # Truncate if necessary (bcrypt limit is 72 bytes)
                if len(password_bytes) > 72:
                    password_bytes = password_bytes[:72]
                password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")
            else:
                raise

        # Create player entity
        player = Player(
            username=Username(username),
            email=Email(email),
            password_hash=password_hash,
            country=country,
            initial_resources=initial_resources or {},
        )

        # Save to repository
        return await self._repository.create(player)
