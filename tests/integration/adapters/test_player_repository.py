"""Integration tests for PlayerRepository."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.adapters.repositories.player_repository import PlayerRepositoryImpl
from app.domain.player import Country, Email, Player, Username
from app.models.player import Base, PlayerModel


@pytest.fixture
async def db_session(db_url: str):
    """Create a database session for testing."""

    engine = create_async_engine(db_url, echo=False)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.mark.integration
class TestPlayerRepositoryImpl:
    """Test PlayerRepositoryImpl with real database."""

    @pytest.mark.asyncio
    async def test_create_player(self, db_session: AsyncSession) -> None:
        """Test creating a player."""
        # Given: a repository
        repo = PlayerRepositoryImpl(session=db_session)

        # When: creating a player
        player = Player(
            username=Username("player123"),
            email=Email("player@example.com"),
            password_hash="hashed_password",
            country=Country.USA,
            initial_resources={"money": 1000, "troops": 100},
        )

        created = await repo.create(player)

        # Then: player is created with ID
        assert created.id == player.id
        assert created.username.value == "player123"
        assert created.email.value == "player@example.com"
        assert created.country == Country.USA
        assert created.initial_resources == {"money": 1000, "troops": 100}

        # Verify in database
        # Refresh the ORM model, not the domain entity
        from sqlalchemy import select

        stmt = select(PlayerModel).where(PlayerModel.id == created.id)
        result = await db_session.execute(stmt)
        db_player = result.scalar_one()
        await db_session.refresh(db_player)
        assert db_player is not None
        assert db_player.username == "player123"
        assert db_player.email == "player@example.com"

    @pytest.mark.asyncio
    async def test_find_by_username(self, db_session: AsyncSession) -> None:
        """Test finding player by username."""
        # Given: a repository and existing player
        repo = PlayerRepositoryImpl(session=db_session)
        player = Player(
            username=Username("player123"),
            email=Email("player@example.com"),
            password_hash="hashed_password",
            country=Country.USA,
        )
        await repo.create(player)

        # When: finding by username
        found = await repo.find_by_username("player123")

        # Then: player is found
        assert found is not None
        assert found.username.value == "player123"
        assert found.email.value == "player@example.com"

    @pytest.mark.asyncio
    async def test_find_by_username_not_found(self, db_session: AsyncSession) -> None:
        """Test finding non-existent username returns None."""
        # Given: a repository
        repo = PlayerRepositoryImpl(session=db_session)

        # When: finding non-existent username
        found = await repo.find_by_username("nonexistent")

        # Then: None is returned
        assert found is None

    @pytest.mark.asyncio
    async def test_find_by_email(self, db_session: AsyncSession) -> None:
        """Test finding player by email."""
        # Given: a repository and existing player
        repo = PlayerRepositoryImpl(session=db_session)
        player = Player(
            username=Username("player123"),
            email=Email("player@example.com"),
            password_hash="hashed_password",
            country=Country.RUSSIA,
        )
        await repo.create(player)

        # When: finding by email
        found = await repo.find_by_email("player@example.com")

        # Then: player is found
        assert found is not None
        assert found.email.value == "player@example.com"
        assert found.country == Country.RUSSIA

    @pytest.mark.asyncio
    async def test_find_by_email_not_found(self, db_session: AsyncSession) -> None:
        """Test finding non-existent email returns None."""
        # Given: a repository
        repo = PlayerRepositoryImpl(session=db_session)

        # When: finding non-existent email
        found = await repo.find_by_email("nonexistent@example.com")

        # Then: None is returned
        assert found is None

    @pytest.mark.asyncio
    async def test_unique_constraint_username(self, db_session: AsyncSession) -> None:
        """Test that duplicate username raises error."""
        # Given: a repository and existing player
        repo = PlayerRepositoryImpl(session=db_session)
        player1 = Player(
            username=Username("player123"),
            email=Email("player1@example.com"),
            password_hash="hash1",
            country=Country.USA,
        )
        await repo.create(player1)

        # When/Then: creating duplicate username raises error
        player2 = Player(
            username=Username("player123"),
            email=Email("player2@example.com"),
            password_hash="hash2",
            country=Country.CHINA,
        )

        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            await repo.create(player2)
            await db_session.flush()  # Ensure error is raised

        # Rollback to clean up for teardown
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_unique_constraint_email(self, db_session: AsyncSession) -> None:
        """Test that duplicate email raises error."""
        # Given: a repository and existing player
        repo = PlayerRepositoryImpl(session=db_session)
        player1 = Player(
            username=Username("player1"),
            email=Email("player@example.com"),
            password_hash="hash1",
            country=Country.USA,
        )
        await repo.create(player1)

        # When/Then: creating duplicate email raises error
        player2 = Player(
            username=Username("player2"),
            email=Email("player@example.com"),
            password_hash="hash2",
            country=Country.EUROPE,
        )

        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            await repo.create(player2)
            await db_session.flush()  # Ensure error is raised

        # Rollback to clean up for teardown
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_initial_resources_jsonb(self, db_session: AsyncSession) -> None:
        """Test that initial_resources is stored as JSONB."""
        # Given: a repository
        repo = PlayerRepositoryImpl(session=db_session)
        resources = {"money": 5000, "troops": 200, "tanks": 10, "aircraft": 5}
        player = Player(
            username=Username("player123"),
            email=Email("player@example.com"),
            password_hash="hashed_password",
            country=Country.USA,
            initial_resources=resources,
        )

        # When: creating player with resources
        created = await repo.create(player)

        # Then: resources are stored correctly
        assert created.initial_resources == resources

        # Verify in database
        db_player = await db_session.get(PlayerModel, created.id)
        assert db_player is not None
        assert db_player.initial_resources == resources
