"""Unit tests for organize command."""

from unittest.mock import Mock, patch

from click.testing import CliRunner

from cli.commands.organize import organize


class TestOrganizeCommand:
    """Test organize command functionality."""

    def test_organize_detects_already_organized(self):
        """Test that organize detects when work is already done."""
        # Red: This test should fail because idempotent detection is not implemented
        with patch('cli.commands.organize.NormPicOrganizer') as mock_organizer_class:
            # Mock organizer to simulate checking if work is already done
            mock_organizer = Mock()
            mock_organizer.is_already_organized.return_value = True
            mock_organizer_class.return_value = mock_organizer

            with patch('cli.commands.organize.validate'):
                runner = CliRunner()
                result = runner.invoke(organize)

                assert result.exit_code == 0
                assert "already organized" in result.output.lower() or "skipping" in result.output.lower()
                # Should not call organize_photos if already organized
                mock_organizer.organize_photos.assert_not_called()

    def test_organize_calls_organize_photos_when_not_organized(self):
        """Test that organize calls organize_photos when work needs to be done."""
        with patch('cli.commands.organize.NormPicOrganizer') as mock_organizer_class:
            # Mock organizer to simulate needing to do work
            mock_organizer = Mock()
            mock_organizer.is_already_organized.return_value = False

            # Mock successful organization result
            mock_result = Mock()
            mock_result.success = True
            mock_result.pics_processed = 5
            mock_result.manifest_path = "/some/path/manifest.json"
            mock_organizer.organize_photos.return_value = mock_result

            mock_organizer_class.return_value = mock_organizer

            with patch('cli.commands.organize.validate'):
                runner = CliRunner()
                result = runner.invoke(organize)

                assert result.exit_code == 0
                # Should call organize_photos when not already organized
                mock_organizer.organize_photos.assert_called_once()
                assert "completed successfully" in result.output.lower()
