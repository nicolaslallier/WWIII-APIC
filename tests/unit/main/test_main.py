"""Unit tests for main application."""

import pytest
from fastapi.testclient import TestClient

from app.main import app, create_app, signal_handler


class TestMainApp:
    """Test main application."""

    def test_create_app(self) -> None:
        """Test app creation."""
        test_app = create_app()
        assert test_app is not None
        assert test_app.title is not None

    def test_healthz_endpoint(self) -> None:
        """Test health check endpoint."""
        client = TestClient(app)
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_readyz_endpoint(self) -> None:
        """Test readiness check endpoint."""
        client = TestClient(app)
        response = client.get("/readyz")
        assert response.status_code == 200
        assert response.json() == {"status": "ready"}

    def test_signal_handler(self) -> None:
        """Test signal handler."""
        import signal
        from unittest.mock import patch

        with patch("sys.exit") as mock_exit:
            signal_handler(signal.SIGTERM, None)
            mock_exit.assert_called_once_with(0)

    @pytest.mark.asyncio
    async def test_lifespan(self) -> None:
        """Test application lifespan context manager."""
        from app.main import lifespan

        async with lifespan(app):
            # App should be running
            pass
        # App should be shut down

