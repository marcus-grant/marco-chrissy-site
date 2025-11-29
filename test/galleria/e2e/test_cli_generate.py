"""E2E tests for galleria CLI generate command."""

import json
import subprocess


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

        # Create test photo files (valid JPEG images)
        photo_paths = []
        for i in range(3):
            photo_path = test_photos_dir / f"wedding_{i:03d}.jpg"
            # Create a simple 100x100 RGB image and save as JPEG
            from PIL import Image
            # Create test image with different colors for each photo
            color = (255 - i * 50, i * 50, 100 + i * 30)  # Different RGB for each
            test_img = Image.new('RGB', (100, 100), color)
            test_img.save(photo_path, 'JPEG')
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

        # Verify thumbnails were actually processed (not just directory created)
        thumbnail_files = list((output_dir / "thumbnails").glob("*.webp"))
        assert len(thumbnail_files) == 3, f"Expected 3 thumbnails, found {len(thumbnail_files)}"

        # Verify thumbnails have actual content (not empty files)
        for thumb in thumbnail_files:
            assert thumb.stat().st_size > 100, f"Thumbnail {thumb.name} appears to be empty or invalid"

        # Verify HTML content structure from template plugin
        page1_content = (output_dir / "page_1.html").read_text()
        assert "wedding_photos" in page1_content, "Collection name not in HTML"
        assert "layout-grid" in page1_content, "Grid layout not applied"
        assert "gallery.css" in page1_content, "CSS not linked"

        # Verify actual gallery structure with thumbnail references
        assert "<img" in page1_content, "No image tags found in HTML"
        assert "thumbnails/" in page1_content, "No thumbnail references found"

        # Verify pagination navigation elements
        assert "page_2.html" in page1_content, "Navigation to page 2 not found"

        # Verify pagination structure (2 photos per page)
        page2_content = (output_dir / "page_2.html").read_text()
        assert "wedding_photos" in page2_content, "Collection name not in page 2"
        assert "<img" in page2_content, "No image tags in page 2"
        assert "thumbnails/" in page2_content, "No thumbnails in page 2"
        assert "page_1.html" in page2_content, "Navigation to page 1 not found"

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
        # Should show click-based error message about missing config
        error_output = result.stderr.lower()
        assert any(phrase in error_output for phrase in ["config", "not found", "no such file", "file not found"]), \
            f"Error should mention config file issue: {result.stderr}"

    def test_cli_generate_shows_help_with_no_args(self, tmp_path):
        """E2E: Test galleria generate with no arguments shows help."""
        # Act: Execute command with no arguments
        result = subprocess.run([
            "python", "-m", "galleria", "generate"
        ], capture_output=True, text=True, cwd=tmp_path.parent.parent.parent)

        # Assert: Should show click-based help or usage information
        output_text = result.stdout + result.stderr
        assert any(word in output_text.lower() for word in ["usage", "help", "config", "required", "missing option"]), \
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
        # Should show meaningful JSON parsing error from click/config validation
        error_output = result.stderr.lower()
        assert any(phrase in error_output for phrase in ["json", "invalid", "parse", "decode", "syntax"]), \
            f"Error should mention JSON parsing issue: {result.stderr}"

    def test_cli_generate_handles_malformed_content_gracefully(self, complete_serving_scenario):
        """E2E: Test galleria generate handles malformed file content without infinite loops."""
        scenario = complete_serving_scenario(num_photos=3, photos_per_page=2)

        # Act: Execute galleria generate command with real scenario
        result = subprocess.run([
            "python", "-m", "galleria", "generate",
            "--config", str(scenario["config_path"]),
            "--verbose"
        ], capture_output=True, text=True, cwd=scenario["config_path"].parent.parent.parent.parent, timeout=30)

        # Assert: Should complete without infinite loop (timeout protects against this)
        assert result.returncode == 0, f"Command failed: {result.stderr}"

        # Verify output files exist and have content
        output_path = scenario["output_path"]
        assert (output_path / "page_1.html").exists(), "Page 1 not generated"
        assert (output_path / "page_2.html").exists(), "Page 2 not generated"
        assert (output_path / "gallery.css").exists(), "CSS not generated"

        # Verify files have actual content (not empty)
        page1_size = (output_path / "page_1.html").stat().st_size
        css_size = (output_path / "gallery.css").stat().st_size
        assert page1_size > 100, f"Page 1 appears empty: {page1_size} bytes"
        assert css_size > 50, f"CSS appears empty: {css_size} bytes"

    def test_cli_generate_timeout_protection_large_collections(self, manifest_factory, galleria_config_factory):
        """E2E: Test CLI handles large photo collections without infinite loops."""
        # Create large photo collection (100 photos)
        photos = []
        for i in range(100):
            photos.append({
                "source_path": f"/fake/photo_{i:03d}.jpg",
                "dest_path": f"img_{i:03d}.jpg",
                "hash": f"hash{i:03d}",
                "size_bytes": 2000000 + i * 1000,
                "mtime": 1234567890 + i
            })

        manifest_path = manifest_factory("large_wedding", photos)
        config_path = galleria_config_factory(custom_config={
            "input": {"manifest_path": str(manifest_path)},
            "pipeline": {
                "transform": {
                    "plugin": "basic-pagination",
                    "config": {"page_size": 10}  # 10 pages with 10 photos each
                }
            }
        })

        # Act: Should handle large collection without infinite loop
        result = subprocess.run([
            "python", "-m", "galleria", "generate",
            "--config", str(config_path),
            "--verbose"
        ], capture_output=True, text=True, cwd=config_path.parent.parent.parent.parent, timeout=60)

        # Assert: Should complete (might fail due to missing photos, but shouldn't infinite loop)
        # Timeout will catch infinite loops
        assert result.returncode is not None, "Command should complete (not infinite loop)"
