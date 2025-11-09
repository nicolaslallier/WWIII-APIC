"""E2E tests for player registration API."""

import pytest
from httpx import ASGITransport, AsyncClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.domain.player import Country
from app.main import app


@pytest.fixture
async def override_db_dependency(db_url: str):
    """Override database session dependency for e2e tests."""
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.db.session import get_db_session
    from app.models.player import Base

    engine = create_async_engine(db_url, echo=False)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def _get_db():
        async with async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db_session] = _get_db
    yield
    app.dependency_overrides.clear()

    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.mark.e2e
class TestPlayerRegistrationAPI:
    """E2E tests for player registration endpoint."""

    @pytest.mark.asyncio
    async def test_register_player_success(self, override_db_dependency) -> None:
        """Test successful player registration."""
        # Given: a client and valid registration data
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            registration_data = {
                "username": "player123",
                "email": "player@example.com",
                "password": "password123",
                "country": Country.USA.value,
                "initial_resources": {"money": 1000, "troops": 100},
            }

            # When: registering a player
            response = await client.post("/api/v1/players/register", json=registration_data)

            # Then: registration succeeds
            assert response.status_code == 201
            data = response.json()
            assert "player" in data
            assert "access_token" in data
            assert data["player"]["username"] == "player123"
            assert data["player"]["email"] == "player@example.com"
            assert data["player"]["country"] == Country.USA.value
            assert "id" in data["player"]
            assert "created_at" in data["player"]

            # Verify JWT token
            settings = get_settings()
            decoded = jwt.decode(
                data["access_token"],
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
            assert decoded["sub"] == str(data["player"]["id"])

    @pytest.mark.asyncio
    async def test_register_player_duplicate_username(self, override_db_dependency) -> None:
        """Test registration fails with duplicate username."""
        # Given: a client and existing player
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            registration_data = {
                "username": "player123",
                "email": "player1@example.com",
                "password": "password123",
                "country": Country.USA.value,
            }

            # Register first player
            await client.post("/api/v1/players/register", json=registration_data)

            # When: registering with duplicate username
            duplicate_data = {
                "username": "player123",
                "email": "player2@example.com",
                "password": "password456",
                "country": Country.RUSSIA.value,
            }
            response = await client.post("/api/v1/players/register", json=duplicate_data)

            # Then: registration fails with 409
            assert response.status_code == 409
            assert "already exists" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_player_duplicate_email(self, override_db_dependency) -> None:
        """Test registration fails with duplicate email."""
        # Given: a client and existing player
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            registration_data = {
                "username": "player1",
                "email": "player@example.com",
                "password": "password123",
                "country": Country.USA.value,
            }

            # Register first player
            await client.post("/api/v1/players/register", json=registration_data)

            # When: registering with duplicate email
            duplicate_data = {
                "username": "player2",
                "email": "player@example.com",
                "password": "password456",
                "country": Country.CHINA.value,
            }
            response = await client.post("/api/v1/players/register", json=duplicate_data)

            # Then: registration fails with 409
            assert response.status_code == 409
            assert "already exists" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_player_validation_errors(self, override_db_dependency) -> None:
        """Test registration validation errors."""
        # Given: a client
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # When: registering with invalid data
            invalid_data = {
                "username": "ab",  # Too short
                "email": "not-an-email",  # Invalid email
                "password": "short",  # Too short
                "country": "INVALID",  # Invalid country
            }
            response = await client.post("/api/v1/players/register", json=invalid_data)

            # Then: validation errors returned
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_player_missing_fields(self, override_db_dependency) -> None:
        """Test registration with missing required fields."""
        # Given: a client
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # When: registering with missing fields
            incomplete_data = {
                "username": "player123",
                # Missing email, password, country
            }
            response = await client.post("/api/v1/players/register", json=incomplete_data)

            # Then: validation errors returned
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_player_default_resources(self, override_db_dependency) -> None:
        """Test registration with default empty resources."""
        # Given: a client
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            registration_data = {
                "username": "player123",
                "email": "player@example.com",
                "password": "password123",
                "country": Country.USA.value,
                # No initial_resources provided
            }

            # When: registering a player
            response = await client.post("/api/v1/players/register", json=registration_data)

            # Then: registration succeeds with default empty resources
            assert response.status_code == 201
            data = response.json()
            assert data["player"]["username"] == "player123"
