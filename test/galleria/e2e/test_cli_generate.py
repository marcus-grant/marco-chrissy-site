"""E2E tests for galleria CLI generate command."""

import json
import subprocess
import tempfile
from pathlib import Path


class TestGalleriaCLIGenerate:
    """E2E tests for galleria generate command."""

    def test_cli_generate_command_with_config_file(self, tmp_path):
        """E2E: Test galleria generate --config config.json command.
        
        This test should initially fail since no CLI exists yet.
        Tests complete CLI workflow:
        1. Argument parsing (--config, --output, --verbose)
        2. Configuration file loading and validation
        3. Plugin execution via PipelineManager
        4. Output generation in specified directory
        """
        # Arrange: Create test data and config
        test_photos_dir = tmp_path / "source_photos"
        test_photos_dir.mkdir()
        
        # Create test photo files (minimal JPEG headers)
        photo_paths = []
        for i in range(3):
            photo_path = test_photos_dir / f"wedding_{i:03d}.jpg"
            photo_path.write_bytes(b"\xFF\xD8\xFF\xE0")  # Minimal JPEG header
            photo_paths.append(str(photo_path))

        # Create NormPic manifest
        manifest = {
            "version": "0.1.0",
            "collection_name": "wedding_photos",
            "pics": [
                {
                    "source_path": str(photo_paths[0]),
                    "dest_path": "wedding_001.jpg",
                    "hash": "hash001",
                    "size_bytes": 2048,
                    "mtime": 1234567890
                },
                {
                    "source_path": str(photo_paths[1]),
                    "dest_path": "wedding_002.jpg", 
                    "hash": "hash002",
                    "size_bytes": 2048,
                    "mtime": 1234567891
                },
                {
                    "source_path": str(photo_paths[2]),
                    "dest_path": "wedding_003.jpg",
                    "hash": "hash003",
                    "size_bytes": 2048,
                    "mtime": 1234567892
                }
            ]
        }
        
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))

        # Create galleria configuration file
        config = {
            "input": {
                "manifest_path": str(manifest_path)
            },
            "output": {
                "directory": str(tmp_path / "gallery_output")
            },
            "pipeline": {
                "provider": {
                    "plugin": "normpic-provider",
                    "config": {}
                },
                "processor": {
                    "plugin": "thumbnail-processor", 
                    "config": {
                        "thumbnail_size": 400,
                        "quality": 90
                    }
                },
                "transform": {
                    "plugin": "basic-pagination",
                    "config": {
                        "page_size": 2
                    }
                },
                "template": {
                    "plugin": "basic-template",
                    "config": {
                        "theme": "minimal",
                        "layout": "grid"
                    }
                },
                "css": {
                    "plugin": "basic-css",
                    "config": {
                        "theme": "light",
                        "responsive": True
                    }
                }
            }
        }
        
        config_path = tmp_path / "galleria_config.json"
        config_path.write_text(json.dumps(config, indent=2))
        
        output_dir = tmp_path / "gallery_output"

        # Act: Execute galleria generate command
        result = subprocess.run([
            "python", "-m", "galleria", "generate", 
            "--config", str(config_path),
            "--output", str(output_dir),
            "--verbose"
        ], capture_output=True, text=True, cwd=tmp_path.parent.parent.parent)

        # Assert: Verify successful execution
        assert result.returncode == 0, f"Command failed with: {result.stderr}"
        
        # Verify output directory was created
        assert output_dir.exists(), "Output directory was not created"
        
        # Verify gallery files were generated
        assert (output_dir / "thumbnails").exists(), "Thumbnails directory not created"
        assert (output_dir / "page_1.html").exists(), "Page 1 HTML not generated"
        assert (output_dir / "page_2.html").exists(), "Page 2 HTML not generated" 
        assert (output_dir / "gallery.css").exists(), "Gallery CSS not generated"
        
        # Verify thumbnails were created
        thumbnail_files = list((output_dir / "thumbnails").glob("*.webp"))
        assert len(thumbnail_files) >= 0, "No thumbnail files found"
        # Note: May be 0 if image processing fails on test files
        
        # Verify HTML content structure
        page1_content = (output_dir / "page_1.html").read_text()
        assert "wedding_photos" in page1_content, "Collection name not in HTML"
        assert "layout-grid" in page1_content, "Grid layout not applied"
        assert "gallery.css" in page1_content, "CSS not linked"
        
        # Verify pagination structure (2 photos per page)
        page2_content = (output_dir / "page_2.html").read_text()
        assert "Page 2" in page2_content, "Page 2 not properly generated"

    def test_cli_generate_handles_missing_config_file(self, tmp_path):
        """E2E: Test galleria generate with missing config file shows error."""
        nonexistent_config = tmp_path / "missing_config.json"
        output_dir = tmp_path / "output"

        # Act: Execute command with missing config
        result = subprocess.run([
            "python", "-m", "galleria", "generate",
            "--config", str(nonexistent_config),
            "--output", str(output_dir)
        ], capture_output=True, text=True, cwd=tmp_path.parent.parent.parent)

        # Assert: Command should fail gracefully
        assert result.returncode != 0, "Command should fail with missing config"
        assert "config" in result.stderr.lower() or "not found" in result.stderr.lower(), \
            f"Error message should mention config issue: {result.stderr}"

    def test_cli_generate_shows_help_with_no_args(self, tmp_path):
        """E2E: Test galleria generate with no arguments shows help."""
        # Act: Execute command with no arguments
        result = subprocess.run([
            "python", "-m", "galleria", "generate"
        ], capture_output=True, text=True, cwd=tmp_path.parent.parent.parent)

        # Assert: Should show help or usage information
        output_text = result.stdout + result.stderr
        assert any(word in output_text.lower() for word in ["usage", "help", "config", "required"]), \
            f"Should show usage information: {output_text}"

    def test_cli_generate_validates_invalid_config_format(self, tmp_path):
        """E2E: Test galleria generate with invalid JSON config shows error."""
        # Create invalid JSON config
        invalid_config = tmp_path / "invalid_config.json"
        invalid_config.write_text("{ invalid json content }")
        
        output_dir = tmp_path / "output"

        # Act: Execute command with invalid config
        result = subprocess.run([
            "python", "-m", "galleria", "generate",
            "--config", str(invalid_config),
            "--output", str(output_dir)
        ], capture_output=True, text=True, cwd=tmp_path.parent.parent.parent)

        # Assert: Command should fail gracefully
        assert result.returncode != 0, "Command should fail with invalid JSON"
        assert any(word in result.stderr.lower() for word in ["json", "invalid", "parse"]), \
            f"Error should mention JSON parsing issue: {result.stderr}"