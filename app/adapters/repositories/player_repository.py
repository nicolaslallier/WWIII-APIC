"""Player repository implementation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.player import Country, Email, Player, Username
from app.models.player import PlayerModel
from app.use_cases.ports import PlayerRepository


class PlayerRepositoryImpl(PlayerRepository):
    """PostgreSQL implementation of PlayerRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize PlayerRepositoryImpl.

        Args:
            session: Database session
        """
        self._session = session

    async def find_by_username(self, username: str) -> Player | None:
        """
        Find player by username.

        Args:
            username: Username to search for

        Returns:
            Player if found, None otherwise
        """
        stmt = select(PlayerModel).where(PlayerModel.username == username)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def find_by_email(self, email: str) -> Player | None:
        """
        Find player by email.

        Args:
            email: Email to search for

        Returns:
            Player if found, None otherwise
        """
        stmt = select(PlayerModel).where(PlayerModel.email == email)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    async def create(self, player: Player) -> Player:
        """
        Create a new player.

        Args:
            player: Player entity to create

        Returns:
            Created player entity
        """
        model = PlayerModel(
            id=player.id,
            username=player.username.value,
            email=player.email.value,
            password_hash=player.password_hash,
            country=player.country.value,
            initial_resources=player.initial_resources,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_domain(model)

    def _to_domain(self, model: PlayerModel) -> Player:
        """
        Convert ORM model to domain entity.

        Args:
            model: ORM model

        Returns:
            Domain entity
        """
        return Player(
            id=model.id,
            username=Username(model.username),
            email=Email(model.email),
            password_hash=model.password_hash,
            country=Country(model.country),
            initial_resources=model.initial_resources or {},
        )
