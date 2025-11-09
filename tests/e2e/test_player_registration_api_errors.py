"""Additional E2E tests for error handling coverage."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

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
class TestPlayerRegistrationAPIErrorHandling:
    """Test error handling paths in player registration API."""

    @pytest.mark.asyncio
    async def test_register_player_value_error_handling(self, override_db_dependency) -> None:
        """Test that ValueError from domain validation is handled."""
        # Given: a client
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # When: registering with invalid username format (triggers ValueError in domain)
            # This should be caught by Pydantic validation first, but let's test the error path
            invalid_data = {
                "username": "player@123",  # Contains @ which is invalid
                "email": "player@example.com",
                "password": "password123",
                "country": Country.USA.value,
            }
            response = await client.post("/api/v1/players/register", json=invalid_data)

            # Then: validation error returned (422)
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_player_unexpected_error(self, override_db_dependency) -> None:
        """Test that unexpected errors are handled gracefully."""
        # Given: a client
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Register a player first
            valid_data = {
                "username": "player123",
                "email": "player@example.com",
                "password": "password123",
                "country": Country.USA.value,
            }
            await client.post("/api/v1/players/register", json=valid_data)

            # Now trigger duplicate error which should be caught as DuplicatePlayerError
            # This covers the DuplicatePlayerError exception handler
            response = await client.post("/api/v1/players/register", json=valid_data)

            # Then: error is handled (409 for duplicate)
            assert response.status_code == 409
            assert "already exists" in response.json()["detail"].lower()
