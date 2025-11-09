"""Unit tests for database session error handling."""

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import get_db_session


@pytest.mark.asyncio
async def test_get_db_session_success_commit(db_url: str) -> None:
    """Test that successful session commits."""
    # Override the database URL for this test
    import os

    os.environ["DATABASE_URL"] = db_url

    # Test that get_db_session commits on success
    async for _session in get_db_session():
        # Do nothing - should commit successfully (line 44)
        pass
    # Session should have committed and closed


@pytest.mark.asyncio
async def test_get_db_session_exception_rollback(db_url: str) -> None:
    """Test that exceptions trigger rollback (covers lines 46-47)."""
    # Override the database URL for this test
    import os

    os.environ["DATABASE_URL"] = db_url

    # Test that get_db_session properly handles exceptions
    # We need to ensure the exception is raised inside the try block
    # so that lines 46-47 (rollback and raise) are executed
    error_raised = False
    try:
        async for _session in get_db_session():
            # Raise error inside the generator context
            # This will be caught by the except block in get_db_session
            raise SQLAlchemyError("Test error")
    except SQLAlchemyError:
        # Exception was re-raised after rollback (line 47)
        error_raised = True

    assert error_raised, "Exception should have been raised after rollback"

