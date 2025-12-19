"""Unit tests for shared theme asset manager.

NOTE: Current implementation downloads latest PicoCSS without version pinning.
This is acceptable for MVP but should be addressed post-MVP for reproducible builds.
See TODO.md Medium-term Features for version pinning implementation.
"""

from unittest.mock import Mock, patch

import pytest


class TestAssetManager:
    """Test shared asset manager functionality."""

    def test_asset_manager_initialization(self, temp_filesystem):
        """Test AssetManager initializes with output directory."""
        from themes.shared.utils.asset_manager import AssetManager

        output_dir = temp_filesystem / "output"
        output_dir.mkdir()

        asset_manager = AssetManager(output_dir)

        assert asset_manager.output_dir == output_dir
        assert asset_manager.css_dir == output_dir / "css"
        assert asset_manager.js_dir == output_dir / "js"

    def test_ensure_asset_downloads_pico_css(self, temp_filesystem):
        """Test ensure_asset downloads PicoCSS to correct location."""
        from themes.shared.utils.asset_manager import AssetManager

        output_dir = temp_filesystem / "output"
        output_dir.mkdir()

        asset_manager = AssetManager(output_dir)

        # Mock the download functionality
        with patch('themes.shared.utils.asset_manager.requests') as mock_requests:
            mock_response = Mock()
            mock_response.text = "/* PicoCSS content */"
            mock_response.raise_for_status = Mock()
            mock_requests.get.return_value = mock_response

            css_path = asset_manager.ensure_asset("pico", "css")

        assert css_path == output_dir / "css" / "pico.min.css"
        assert css_path.exists()
        assert css_path.read_text() == "/* PicoCSS content */"

        # Verify correct URL was requested (latest version - no pinning for MVP)
        mock_requests.get.assert_called_once_with(
            "https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css",
            timeout=30
        )

    def test_ensure_asset_skips_download_if_exists(self, temp_filesystem):
        """Test ensure_asset skips download if file already exists."""
        from themes.shared.utils.asset_manager import AssetManager

        output_dir = temp_filesystem / "output"
        css_dir = output_dir / "css"
        css_dir.mkdir(parents=True)

        # Create existing file
        existing_css = css_dir / "pico.min.css"
        existing_css.write_text("/* Existing PicoCSS */")

        asset_manager = AssetManager(output_dir)

        with patch('themes.shared.utils.asset_manager.requests') as mock_requests:
            css_path = asset_manager.ensure_asset("pico", "css")

        assert css_path == existing_css
        assert css_path.read_text() == "/* Existing PicoCSS */"

        # Should not have made HTTP request
        mock_requests.get.assert_not_called()

    def test_ensure_asset_creates_directories_if_missing(self, temp_filesystem):
        """Test ensure_asset creates output directories as needed."""
        from themes.shared.utils.asset_manager import AssetManager

        output_dir = temp_filesystem / "output"
        # Note: not creating output_dir to test directory creation

        asset_manager = AssetManager(output_dir)

        with patch('themes.shared.utils.asset_manager.requests') as mock_requests:
            mock_response = Mock()
            mock_response.text = "/* CSS content */"
            mock_response.raise_for_status = Mock()
            mock_requests.get.return_value = mock_response

            css_path = asset_manager.ensure_asset("pico", "css")

        assert output_dir.exists()
        assert (output_dir / "css").exists()
        assert css_path.exists()

    def test_ensure_asset_handles_download_failure(self, temp_filesystem):
        """Test ensure_asset handles HTTP errors gracefully."""
        from themes.shared.utils.asset_manager import AssetManager

        output_dir = temp_filesystem / "output"
        output_dir.mkdir()

        asset_manager = AssetManager(output_dir)

        with patch('themes.shared.utils.asset_manager.requests') as mock_requests:
            mock_requests.get.side_effect = Exception("Network error")

            with pytest.raises(Exception) as exc_info:
                asset_manager.ensure_asset("pico", "css")

            assert "Failed to download asset pico" in str(exc_info.value)

    def test_ensure_asset_unknown_asset_raises_error(self, temp_filesystem):
        """Test ensure_asset raises error for unknown asset types."""
        from themes.shared.utils.asset_manager import AssetManager

        output_dir = temp_filesystem / "output"
        output_dir.mkdir()

        asset_manager = AssetManager(output_dir)

        with pytest.raises(ValueError) as exc_info:
            asset_manager.ensure_asset("unknown", "css")

        assert "Unknown asset: unknown" in str(exc_info.value)

    def test_ensure_asset_unknown_file_type_raises_error(self, temp_filesystem):
        """Test ensure_asset raises error for unknown file types."""
        from themes.shared.utils.asset_manager import AssetManager

        output_dir = temp_filesystem / "output"
        output_dir.mkdir()

        asset_manager = AssetManager(output_dir)

        with pytest.raises(ValueError) as exc_info:
            asset_manager.ensure_asset("pico", "unknown")

        assert "Unknown file type: unknown" in str(exc_info.value)

    def test_get_asset_url_returns_correct_path(self, temp_filesystem):
        """Test get_asset_url returns correct relative URL path."""
        from themes.shared.utils.asset_manager import AssetManager

        output_dir = temp_filesystem / "output"
        output_dir.mkdir()

        asset_manager = AssetManager(output_dir)

        css_url = asset_manager.get_asset_url("pico", "css")
        assert css_url == "/css/pico.min.css"

        js_url = asset_manager.get_asset_url("pico", "js")
        assert js_url == "/js/pico.min.js"

    def test_get_shared_css_files_finds_css_files(self, temp_filesystem):
        """Test get_shared_css_files finds CSS files from default paths."""
        from themes.shared.utils.asset_manager import AssetManager

        output_dir = temp_filesystem / "output"
        output_dir.mkdir()

        # Create shared CSS directory with test files
        shared_css_dir = temp_filesystem / "themes" / "shared" / "css"
        shared_css_dir.mkdir(parents=True)

        # Create test CSS files
        (shared_css_dir / "shared.css").write_text(".shared { color: blue; }")
        (shared_css_dir / "navigation.css").write_text(".nav { background: red; }")
        (shared_css_dir / "ignore.txt").write_text("Not CSS")  # Should be ignored

        # Mock defaults to use our test directory
        with patch('themes.shared.utils.asset_manager.get_shared_css_paths') as mock_paths:
            mock_paths.return_value = [shared_css_dir]

            asset_manager = AssetManager(output_dir)
            css_files = asset_manager.get_shared_css_files()

        assert len(css_files) == 2
        css_names = [f.name for f in css_files]
        assert "shared.css" in css_names
        assert "navigation.css" in css_names
        assert "ignore.txt" not in css_names

    def test_copy_shared_css_files_copies_to_output(self, temp_filesystem):
        """Test copy_shared_css_files copies CSS files to output directory."""
        from themes.shared.utils.asset_manager import AssetManager

        output_dir = temp_filesystem / "output"
        output_dir.mkdir()

        # Create shared CSS directory with test files
        shared_css_dir = temp_filesystem / "themes" / "shared" / "css"
        shared_css_dir.mkdir(parents=True)

        # Create test CSS files
        (shared_css_dir / "shared.css").write_text(".shared-nav { color: blue; background: red; }")
        (shared_css_dir / "components.css").write_text(".button { padding: 10px; }")

        # Mock defaults to use our test directory
        with patch('themes.shared.utils.asset_manager.get_shared_css_paths') as mock_paths:
            mock_paths.return_value = [shared_css_dir]

            asset_manager = AssetManager(output_dir)
            copied_files = asset_manager.copy_shared_css_files()

        # Verify files were copied
        assert len(copied_files) == 2

        # Check output files exist and have correct content
        output_shared_css = output_dir / "css" / "shared.css"
        output_components_css = output_dir / "css" / "components.css"

        assert output_shared_css.exists()
        assert output_components_css.exists()

        assert output_shared_css.read_text() == ".shared-nav { color: blue; background: red; }"
        assert output_components_css.read_text() == ".button { padding: 10px; }"

        # Verify returned paths are correct
        copied_names = [f.name for f in copied_files]
        assert "shared.css" in copied_names
        assert "components.css" in copied_names
