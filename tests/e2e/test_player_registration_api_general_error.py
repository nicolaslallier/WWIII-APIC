"""E2E test for general exception handling in player registration."""

from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.domain.player import Country
from app.main import app


@pytest.fixture
async def override_db_dependency(db_url: str):
    """Override database session dependency for e2e tests."""
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

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
@pytest.mark.asyncio
async def test_register_player_general_exception(override_db_dependency) -> None:
    """Test that general exceptions are handled gracefully."""
    # Given: a client
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Patch the use case execute method to raise a general exception
        from app.api.v1.players import get_register_player_use_case

        async def mock_execute(*args, **kwargs):
            raise RuntimeError("Unexpected error")

        # Create a mock use case
        mock_use_case = AsyncMock()
        mock_use_case.execute = mock_execute

        # Patch the dependency
        app.dependency_overrides[get_register_player_use_case] = lambda: mock_use_case

        try:
            registration_data = {
                "username": "player123",
                "email": "player@example.com",
                "password": "password123",
                "country": Country.USA.value,
            }

            # When: registering (should trigger general exception handler)
            response = await client.post("/api/v1/players/register", json=registration_data)

            # Then: 500 error returned
            assert response.status_code == 500
            assert "unexpected error" in response.json()["detail"].lower()
        finally:
            # Clean up
            app.dependency_overrides.pop(get_register_player_use_case, None)


