"""Test defaults module for path configuration."""

from pathlib import Path

from defaults import get_output_dir


class TestDefaults:
    """Test defaults module path configuration functions."""

    def test_get_output_dir_returns_path_object(self):
        """Test get_output_dir returns Path object, not string."""
        result = get_output_dir()
        assert isinstance(result, Path)
        assert str(result) == "output"

    def test_get_output_dir_returns_output_directory(self):
        """Test get_output_dir returns the output directory."""
        result = get_output_dir()
        assert result == Path("output")
