"""Unit tests for domain entity edge cases."""


from app.domain.player import Country, Email, Player, Username


class TestEmailEdgeCases:
    """Test Email value object edge cases."""

    def test_email_eq_with_non_email(self) -> None:
        """Test that Email.__eq__ returns False for non-Email objects."""
        email = Email("test@example.com")
        assert email != "test@example.com"
        assert email != 123
        assert email != None  # noqa: E711

    def test_email_hash(self) -> None:
        """Test that Email can be hashed."""
        email = Email("test@example.com")
        hash(email)  # Should not raise


class TestUsernameEdgeCases:
    """Test Username value object edge cases."""

    def test_username_eq_with_non_username(self) -> None:
        """Test that Username.__eq__ returns False for non-Username objects."""
        username = Username("testuser")
        assert username != "testuser"
        assert username != 123
        assert username != None  # noqa: E711

    def test_username_hash(self) -> None:
        """Test that Username can be hashed."""
        username = Username("testuser")
        hash(username)  # Should not raise


class TestPlayerEdgeCases:
    """Test Player entity edge cases."""

    def test_player_eq_with_non_player(self) -> None:
        """Test that Player.__eq__ returns False for non-Player objects."""
        player = Player(
            username=Username("testuser"),
            email=Email("test@example.com"),
            password_hash="hash",
            country=Country.USA,
        )
        assert player != "testuser"
        assert player != 123
        assert player != None  # noqa: E711

    def test_player_hash(self) -> None:
        """Test that Player can be hashed."""
        player = Player(
            username=Username("testuser"),
            email=Email("test@example.com"),
            password_hash="hash",
            country=Country.USA,
        )
        hash(player)  # Should not raise

    def test_player_repr(self) -> None:
        """Test Player string representation."""
        player = Player(
            username=Username("testuser"),
            email=Email("test@example.com"),
            password_hash="hash",
            country=Country.USA,
        )
        repr_str = repr(player)
        assert "Player" in repr_str
        assert "testuser" in repr_str

