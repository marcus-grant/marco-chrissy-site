"""Unit tests for build exceptions."""

import pytest

from build.exceptions import BuildError, ConfigError, GalleriaError, PelicanError


class TestBuildExceptions:
    """Test build exception hierarchy."""

    def test_build_error_is_base_exception(self):
        """Test that BuildError is the base exception."""
        error = BuildError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_config_error_inherits_from_build_error(self):
        """Test that ConfigError inherits from BuildError."""
        error = ConfigError("Config error")
        assert str(error) == "Config error"
        assert isinstance(error, BuildError)
        assert isinstance(error, Exception)

    def test_galleria_error_inherits_from_build_error(self):
        """Test that GalleriaError inherits from BuildError."""
        error = GalleriaError("Galleria error")
        assert str(error) == "Galleria error"
        assert isinstance(error, BuildError)
        assert isinstance(error, Exception)

    def test_pelican_error_inherits_from_build_error(self):
        """Test that PelicanError inherits from BuildError."""
        error = PelicanError("Pelican error")
        assert str(error) == "Pelican error"
        assert isinstance(error, BuildError)
        assert isinstance(error, Exception)

    def test_exceptions_can_be_raised_and_caught_specifically(self):
        """Test that exceptions can be raised and caught by specific type."""
        # Test ConfigError
        with pytest.raises(ConfigError) as exc_info:
            raise ConfigError("Config failed")
        assert "Config failed" in str(exc_info.value)

        # Test GalleriaError
        with pytest.raises(GalleriaError) as exc_info:
            raise GalleriaError("Galleria failed")
        assert "Galleria failed" in str(exc_info.value)

        # Test PelicanError
        with pytest.raises(PelicanError) as exc_info:
            raise PelicanError("Pelican failed")
        assert "Pelican failed" in str(exc_info.value)

    def test_exceptions_can_be_caught_as_build_error(self):
        """Test that specific exceptions can be caught as BuildError."""
        # ConfigError can be caught as BuildError
        with pytest.raises(BuildError):
            raise ConfigError("Config failed")

        # GalleriaError can be caught as BuildError
        with pytest.raises(BuildError):
            raise GalleriaError("Galleria failed")

        # PelicanError can be caught as BuildError
        with pytest.raises(BuildError):
            raise PelicanError("Pelican failed")

    def test_exceptions_support_chaining(self):
        """Test that exceptions support exception chaining."""
        original_error = ValueError("Original error")
        
        # Test with from clause
        with pytest.raises(ConfigError) as exc_info:
            try:
                raise original_error
            except ValueError as e:
                raise ConfigError("Config loading failed") from e
        
        assert exc_info.value.__cause__ is original_error
        assert "Config loading failed" in str(exc_info.value)