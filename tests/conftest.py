"""Shared pytest fixtures and configuration."""
import asyncio
from typing import AsyncGenerator, Generator

import pytest
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """Create a PostgreSQL testcontainer for integration tests."""
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture
async def db_url(postgres_container: PostgresContainer) -> str:
    """Get database URL from testcontainer."""
    return postgres_container.get_connection_url().replace("postgresql://", "postgresql+asyncpg://")


@pytest.fixture
def anyio_backend() -> str:
    """Use asyncio backend for anyio."""
    return "asyncio"

