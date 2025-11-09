"""Unit test for database session rollback using mocks."""

from unittest.mock import AsyncMock, patch

import pytest

from app.db.session import get_db_session


@pytest.mark.asyncio
async def test_get_db_session_rollback_with_mock(db_url: str) -> None:
    """Test rollback path using mocks to ensure coverage (covers lines 46-47)."""
    import os

    os.environ["DATABASE_URL"] = db_url

    # Mock the session to raise an error on commit
    # This will trigger the except block (lines 46-47)
    with patch('app.db.session.async_session_maker') as mock_session_maker:
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        # Make commit raise an exception
        mock_session.commit = AsyncMock(side_effect=Exception("Commit failed"))
        mock_session.rollback = AsyncMock()

        mock_session_maker.return_value = mock_session

        # Now test the rollback path
        error_raised = False
        try:
            async for _session in get_db_session():
                # Session is yielded, then commit will fail
                pass
        except Exception:
            # Exception was re-raised after rollback (line 47)
            error_raised = True

        assert error_raised, "Exception should have been raised"
        # Verify rollback was called (line 46)
        mock_session.rollback.assert_awaited_once()

