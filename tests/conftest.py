"""Shared pytest fixtures and configuration."""

import asyncio
import os
from collections.abc import Generator

import pytest
from testcontainers.postgres import PostgresContainer

# Set environment variables before any imports that might use Settings
# This runs at module import time, before pytest collection
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing-only")

# Patch passlib's bcrypt wrap bug detection to avoid initialization errors
# This is safe as modern bcrypt doesn't have the wrap bug
try:
    import passlib.handlers.bcrypt as bcrypt_module

    # The wrap bug detection happens in _finalize_backend_mixin
    # We'll patch it at the class level if possible
    if hasattr(bcrypt_module, "_BcryptBackend"):
        original_finalize = bcrypt_module._BcryptBackend._finalize_backend_mixin

        def patched_finalize(cls, name, dryrun=False):
            # Skip wrap bug detection by calling parent implementation
            # or by setting a flag that prevents detection
            result = original_finalize(cls, name, dryrun)
            # If detection was attempted and failed, we'll handle it in the use case
            return result

        # Only patch if we can safely do so
        # Actually, let's just let it fail and handle it in the use case code
        pass
except (ImportError, AttributeError):
    # passlib not available or structure different, skip patching
    pass


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
    url = postgres_container.get_connection_url()
    # Convert to asyncpg URL format
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://")
    elif url.startswith("postgresql+psycopg2://"):
        url = url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")
    return url


@pytest.fixture
def anyio_backend() -> str:
    """Use asyncio backend for anyio."""
    return "asyncio"
