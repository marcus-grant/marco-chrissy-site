"""E2E tests for site build command."""

import json
import os
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from click.testing import CliRunner

from cli.commands.build import build


class TestSiteBuild:
    """Test the site build command functionality."""

    @pytest.mark.skip(reason="Build command functionality not yet implemented")
    def test_build_complete_workflow(self, temp_filesystem, full_config_setup, fake_image_factory):
        """Test complete build workflow: organize → galleria → pelican with idempotency."""
        
        # Setup: Create source directory with test photos
        fake_image_factory("IMG_001.jpg", directory="source_photos", use_raw_bytes=True)
        fake_image_factory("IMG_002.jpg", directory="source_photos", use_raw_bytes=True)
        fake_image_factory("IMG_003.jpg", directory="source_photos", use_raw_bytes=True)

        # Setup: Configure complete pipeline
        full_config_setup({
            "normpic": {
                "source_dir": str(temp_filesystem / "source_photos"),
                "dest_dir": str(temp_filesystem / "output" / "pics" / "full"),
                "collection_name": "wedding", 
                "collection_description": "Test wedding photos",
                "create_symlinks": True
            },
            "galleria": {
                "input": {
                    "manifest_path": str(temp_filesystem / "output" / "pics" / "full" / "manifest.json")
                },
                "output": {
                    "directory": str(temp_filesystem / "output" / "galleries" / "wedding")
                },
                "pipeline": {
                    "provider": {"plugin": "normpic-provider"},
                    "processor": {"plugin": "thumbnail-processor", "config": {"thumbnail_size": 400}},
                    "transform": {"plugin": "basic-pagination", "config": {"page_size": 12}},
                    "template": {"plugin": "basic-template", "config": {"title": "Wedding Gallery"}},
                    "css": {"plugin": "basic-css"}
                }
            },
            "pelican": {
                "content_dir": str(temp_filesystem / "content"),
                "output_dir": str(temp_filesystem / "output"),
                "theme": "simple"
            }
        })

        # First Run: Initial build
        original_cwd = os.getcwd()
        try:
            os.chdir(str(temp_filesystem))
            runner = CliRunner()
            result1 = runner.invoke(build)
        finally:
            os.chdir(original_cwd)

        # Assert: Command succeeded and shows expected workflow
        assert result1.exit_code == 0, f"Initial build failed: {result1.output}"
        assert "validation" in result1.output.lower(), "Should show validation cascade"
        assert "organize" in result1.output.lower(), "Should show organize cascade"
        assert "galleria" in result1.output.lower(), "Should show galleria generation"
        assert "pelican" in result1.output.lower(), "Should show pelican generation"

        # Assert: Expected directory structure created
        output_dir = temp_filesystem / "output"
        pics_dir = output_dir / "pics" / "full"
        galleries_dir = output_dir / "galleries" / "wedding"
        
        assert pics_dir.exists(), f"Photos directory not created: {pics_dir}"
        assert galleries_dir.exists(), f"Galleries directory not created: {galleries_dir}"
        assert (output_dir / "index.html").exists(), "Site index not created"

        # Assert: Manifest created from organize step
        manifest_path = pics_dir / "manifest.json"
        assert manifest_path.exists(), f"Manifest not created: {manifest_path}"
        
        with open(manifest_path) as f:
            manifest_data = json.load(f)
        assert manifest_data["collection_name"] == "wedding"
        assert len(manifest_data["pics"]) == 3

        # Assert: Galleria HTML generated with expected content
        gallery_pages = list(galleries_dir.glob("page_*.html"))
        assert len(gallery_pages) >= 1, f"No gallery pages found in {galleries_dir}"

        # Parse gallery HTML and verify content
        gallery_html = gallery_pages[0].read_text()
        soup = BeautifulSoup(gallery_html, 'html.parser')
        
        # Should have gallery structure
        assert soup.find('title'), "Gallery should have title"
        assert "Wedding Gallery" in soup.find('title').text, "Title should match config"
        
        # Should have image references
        img_elements = soup.find_all('img')
        assert len(img_elements) >= 3, f"Should have 3 images, found {len(img_elements)}"
        
        # Should have CSS references
        css_links = soup.find_all('link', rel='stylesheet')
        assert len(css_links) >= 1, "Should have CSS stylesheet links"

        # Assert: Thumbnails directory created
        thumbnails_dir = galleries_dir / "thumbnails"
        assert thumbnails_dir.exists(), f"Thumbnails directory not created: {thumbnails_dir}"
        
        thumbnail_files = list(thumbnails_dir.glob("*.webp"))
        assert len(thumbnail_files) >= 3, f"Should have 3 thumbnails, found {len(thumbnail_files)}"

        # Assert: Pelican site pages generated
        assert (output_dir / "index.html").exists(), "Site index should exist"
        
        # Parse site index
        index_html = (output_dir / "index.html").read_text()
        index_soup = BeautifulSoup(index_html, 'html.parser')
        assert index_soup.find('title'), "Site index should have title"

        # Second Run: Test idempotency
        try:
            os.chdir(str(temp_filesystem))
            runner = CliRunner()
            result2 = runner.invoke(build)
        finally:
            os.chdir(original_cwd)

        # Assert: Second run is idempotent
        assert result2.exit_code == 0, f"Idempotent build failed: {result2.output}"
        assert ("already built" in result2.output.lower() or 
                "skipping" in result2.output.lower() or
                "up to date" in result2.output.lower()), "Should skip unnecessary work"