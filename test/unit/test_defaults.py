"""Test defaults module for path configuration."""

from pathlib import Path

from defaults import get_output_dir, get_shared_css_paths, get_shared_template_paths


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

    def test_get_shared_template_paths_returns_path_objects(self):
        """Test get_shared_template_paths returns list of Path objects."""
        result = get_shared_template_paths()
        assert isinstance(result, list)
        assert len(result) > 0
        for path in result:
            assert isinstance(path, Path)

    def test_get_shared_template_paths_contains_expected_paths(self):
        """Test get_shared_template_paths contains expected template directories."""
        result = get_shared_template_paths()
        expected_paths = [
            Path("themes/shared/templates"),
            Path("themes/shared/components"),
        ]
        for expected_path in expected_paths:
            assert expected_path in result

    def test_get_shared_css_paths_returns_path_objects(self):
        """Test get_shared_css_paths returns list of Path objects."""
        result = get_shared_css_paths()
        assert isinstance(result, list)
        assert len(result) > 0
        for path in result:
            assert isinstance(path, Path)

    def test_get_shared_css_paths_contains_expected_paths(self):
        """Test get_shared_css_paths contains expected CSS directories."""
        result = get_shared_css_paths()
        expected_paths = [
            Path("themes/shared/css"),
        ]
        for expected_path in expected_paths:
            assert expected_path in result
