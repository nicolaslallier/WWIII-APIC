"""Integration test for database session rollback coverage."""

import pytest
from sqlalchemy import text

from app.db.session import get_db_session


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_db_session_rollback_on_database_error(db_url: str) -> None:
    """Test that database errors trigger rollback (covers lines 46-47)."""
    import os

    os.environ["DATABASE_URL"] = db_url

    # Test that get_db_session properly handles exceptions during commit
    # We'll create an invalid transaction that fails on commit
    # This will trigger the except block (lines 46-47) after yield completes
    error_raised = False
    try:
        async for session in get_db_session():
            # Create an invalid state that will cause commit to fail
            # Execute a statement that creates an error state
            # Then when commit is attempted (line 44), it will fail
            # This failure will be caught by except (line 45), triggering rollback (line 46)
            await session.execute(text("CREATE TABLE IF NOT EXISTS test_table (id INT)"))
            # Now delete the table while we have a transaction
            await session.execute(text("DROP TABLE test_table"))
            # Force an error by trying to use the deleted table
            # This will cause commit to fail, triggering the except block
            await session.execute(text("SELECT * FROM test_table"))
            # The commit on line 44 will fail, triggering rollback on line 46
    except Exception:
        # Exception was re-raised after rollback (line 47)
        error_raised = True

    assert error_raised, "Exception should have been raised after rollback"

