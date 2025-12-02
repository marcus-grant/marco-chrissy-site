"""Tests for Galleria CLI with proper mocks."""

import json
from unittest.mock import Mock, patch

from click.testing import CliRunner

from galleria.__main__ import cli
from galleria.plugins.base import PluginResult


class TestGalleriaCLI:
    """Test CLI with proper mocking."""

    def test_generate_command_success_with_mocked_pipeline(self, tmp_path):
        """Test successful generate command with mocked pipeline."""
        # Arrange
        runner = CliRunner()
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(
            '{"version": "0.1.0", "collection_name": "test", "pics": []}'
        )

        config_data = {
            "manifest_path": str(manifest_path),
            "output_dir": str(tmp_path / "output"),
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_data))

        # Mock successful pipeline execution
        mock_result = PluginResult(
            success=True,
            output_data={
                "collection_name": "test",
                "html_files": [
                    {"filename": "page_1.html", "content": "<html>Page 1</html>"},
                    {"filename": "page_2.html", "content": "<html>Page 2</html>"},
                ],
                "css_files": [
                    {"filename": "gallery.css", "content": ".gallery {}"},
                    {"filename": "theme.css", "content": ".theme {}"},
                ],
                "thumbnail_count": 5,
            },
            errors=[],
            metadata={},
        )

        with patch("galleria.__main__.PipelineManager") as mock_pipeline_class:
            mock_pipeline = Mock()
            mock_pipeline_class.return_value = mock_pipeline
            mock_pipeline.execute_stages.return_value = mock_result
            mock_pipeline.registry.register = Mock()

            # Act
            result = runner.invoke(cli, ["generate", "--config", str(config_path)])

            # Assert
            assert result.exit_code == 0
            assert "Gallery generated successfully" in result.output
            assert "Generated 2 HTML pages for 'test'" in result.output
            assert "Generated 2 CSS files" in result.output
            assert "Processed 5 thumbnails" in result.output

            # Verify pipeline was configured correctly
            mock_pipeline.registry.register.assert_any_call(
                mock_pipeline.registry.register.call_args_list[0][0][0], "provider"
            )
            mock_pipeline.execute_stages.assert_called_once()

    def test_generate_command_pipeline_failure(self, tmp_path):
        """Test generate command handles pipeline failure gracefully."""
        # Arrange
        runner = CliRunner()
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(
            '{"version": "0.1.0", "collection_name": "test", "pics": []}'
        )

        config_data = {
            "manifest_path": str(manifest_path),
            "output_dir": str(tmp_path / "output"),
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_data))

        # Mock pipeline failure
        mock_result = PluginResult(
            success=False,
            output_data={},
            errors=["Provider plugin failed", "Invalid manifest format"],
            metadata={},
        )

        with patch("galleria.__main__.PipelineManager") as mock_pipeline_class:
            mock_pipeline = Mock()
            mock_pipeline_class.return_value = mock_pipeline
            mock_pipeline.execute_stages.return_value = mock_result
            mock_pipeline.registry.register = Mock()

            # Act
            result = runner.invoke(cli, ["generate", "--config", str(config_path)])

            # Assert
            assert result.exit_code == 1
            assert "Pipeline execution failed" in result.output
            assert "Provider plugin failed" in result.output
            assert "Invalid manifest format" in result.output

    def test_generate_command_with_verbose_output(self, tmp_path):
        """Test verbose output shows detailed progress."""
        # Arrange
        runner = CliRunner()
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(
            '{"version": "0.1.0", "collection_name": "test", "pics": []}'
        )

        config_data = {
            "manifest_path": str(manifest_path),
            "output_dir": str(tmp_path / "output"),
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_data))

        mock_result = PluginResult(
            success=True,
            output_data={"collection_name": "test"},
            errors=[],
            metadata={},
        )

        with patch("galleria.__main__.PipelineManager") as mock_pipeline_class:
            mock_pipeline = Mock()
            mock_pipeline_class.return_value = mock_pipeline
            mock_pipeline.execute_stages.return_value = mock_result
            mock_pipeline.registry.register = Mock()

            # Act
            result = runner.invoke(
                cli, ["generate", "--config", str(config_path), "--verbose"]
            )

            # Assert
            assert result.exit_code == 0
            assert "Loading configuration from:" in result.output
            assert "Configuration loaded and validated successfully" in result.output
            assert "Initializing plugin pipeline..." in result.output
            assert "Executing plugin pipeline:" in result.output
            assert "[1/5] Running provider (normpic-provider)..." in result.output
            assert "[5/5] Running css (basic-css)..." in result.output
            assert "Pipeline execution completed successfully" in result.output

    def test_generate_command_with_output_override(self, tmp_path):
        """Test output directory override works correctly."""
        # Arrange
        runner = CliRunner()
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(
            '{"version": "0.1.0", "collection_name": "test", "pics": []}'
        )

        config_data = {
            "manifest_path": str(manifest_path),
            "output_dir": str(tmp_path / "original_output"),
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_data))
        override_output = tmp_path / "override_output"

        mock_result = PluginResult(
            success=True,
            output_data={"collection_name": "test"},
            errors=[],
            metadata={},
        )

        with patch("galleria.__main__.PipelineManager") as mock_pipeline_class:
            mock_pipeline = Mock()
            mock_pipeline_class.return_value = mock_pipeline
            mock_pipeline.execute_stages.return_value = mock_result
            mock_pipeline.registry.register = Mock()

            # Act
            result = runner.invoke(
                cli,
                [
                    "generate",
                    "--config",
                    str(config_path),
                    "--output",
                    str(override_output),
                    "--verbose",
                ],
            )

            # Assert
            assert result.exit_code == 0
            assert f"Output directory override: {override_output}" in result.output
            assert str(override_output) in result.output

            # Verify pipeline context used override output
            call_args = mock_pipeline.execute_stages.call_args
            context = call_args[0][1]  # Second argument is the context
            assert context.output_dir == override_output

    def test_generate_command_configuration_error(self, tmp_path):
        """Test configuration error handling."""
        runner = CliRunner()

        # Create config with missing required fields
        config_data = {
            "output_dir": str(tmp_path / "output")
            # Missing manifest_path
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_data))

        # Act
        result = runner.invoke(cli, ["generate", "--config", str(config_path)])

        # Assert
        assert result.exit_code == 1
        assert "Missing required field: manifest_path" in result.output

    def test_generate_command_missing_manifest_file(self, tmp_path):
        """Test error handling for missing manifest file."""
        runner = CliRunner()

        config_data = {
            "manifest_path": str(tmp_path / "missing_manifest.json"),
            "output_dir": str(tmp_path / "output"),
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_data))

        # Act
        result = runner.invoke(cli, ["generate", "--config", str(config_path)])

        # Assert
        assert result.exit_code == 1
        assert "Manifest file not found" in result.output

    def test_generate_command_pipeline_exception(self, tmp_path):
        """Test handling of unexpected pipeline exceptions."""
        # Arrange
        runner = CliRunner()
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(
            '{"version": "0.1.0", "collection_name": "test", "pics": []}'
        )

        config_data = {
            "manifest_path": str(manifest_path),
            "output_dir": str(tmp_path / "output"),
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_data))

        with patch("galleria.__main__.PipelineManager") as mock_pipeline_class:
            mock_pipeline = Mock()
            mock_pipeline_class.return_value = mock_pipeline
            mock_pipeline.execute_stages.side_effect = Exception(
                "Unexpected pipeline error"
            )
            mock_pipeline.registry.register = Mock()

            # Act
            result = runner.invoke(cli, ["generate", "--config", str(config_path)])

            # Assert
            assert result.exit_code == 1
            assert (
                "Pipeline execution error: Unexpected pipeline error" in result.output
            )
