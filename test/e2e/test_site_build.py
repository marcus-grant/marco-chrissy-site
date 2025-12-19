"""E2E tests for site build command."""

import json
import os

from bs4 import BeautifulSoup
from click.testing import CliRunner

from cli.commands.build import build


def setup_shared_theme_structure(directory_factory, file_factory):
    """Create shared theme structure used by both tests."""
    # Create theme directories
    directory_factory("themes/site/templates")
    directory_factory("themes/shared/templates")
    
    # Create shared navbar component
    file_factory(
        "themes/shared/templates/navbar.html",
        '<nav id="test-shared-navbar"><a href="/">Home</a><a href="/about/">About</a><a href="/galleries/wedding/">Gallery</a></nav>'
    )
    
    # Create custom site theme that includes shared navbar
    file_factory(
        "themes/site/templates/base.html",
        """<!DOCTYPE html>
<html lang="en">
<head>
    <title>{{ SITENAME }}</title>
    {% if CSS_FILE %}<link rel="stylesheet" href="{{ SITEURL }}/{{ THEME_STATIC_DIR }}/css/{{ CSS_FILE }}" />{% endif %}
</head>
<body>
    <header>
        <h1><a href="{{ SITEURL }}/">{{ SITENAME }}</a></h1>
        {% include 'navbar.html' %}
    </header>
    <main>{% block content %}{% endblock %}</main>
</body>
</html>"""
    )
    
    file_factory(
        "themes/site/templates/article.html",
        """{% extends "base.html" %}
{% block content %}{{ article.content }}{% endblock %}"""
    )
    
    file_factory(
        "themes/site/templates/index.html",
        """{% extends "base.html" %}
{% block content %}{% for article in articles %}{{ article.content }}{% endfor %}{% endblock %}"""
    )


class TestSiteBuild:
    """Test the site build command functionality."""

    def test_build_uses_orchestrator_pattern(
        self, temp_filesystem, full_config_setup, fake_image_factory, directory_factory, file_factory
    ):
        """Test complete build workflow: organize → galleria → pelican with idempotency."""

        # Setup: Create source directory with test photos
        fake_image_factory("IMG_001.jpg", directory="source_photos", use_raw_bytes=True)
        fake_image_factory("IMG_002.jpg", directory="source_photos", use_raw_bytes=True)
        fake_image_factory("IMG_003.jpg", directory="source_photos", use_raw_bytes=True)

        # Setup: Create content and theme structure
        directory_factory("content")
        setup_shared_theme_structure(directory_factory, file_factory)

        # Setup: Configure complete pipeline
        full_config_setup(
            {
                "normpic": {
                    "source_dir": str(temp_filesystem / "source_photos"),
                    "dest_dir": str(temp_filesystem / "output" / "pics" / "full"),
                    "collection_name": "wedding",
                    "collection_description": "Test wedding photos",
                    "create_symlinks": True,
                },
                "galleria": {
                    "manifest_path": str(
                        temp_filesystem / "output" / "pics" / "full" / "manifest.json"
                    ),
                    "output_dir": str(
                        temp_filesystem / "output" / "galleries" / "wedding"
                    ),
                    "thumbnail_size": 400,
                    "photos_per_page": 12,
                    "theme": "minimal",
                    "quality": 85,
                },
                "pelican": {
                    "theme": "themes/site",
                    "site_url": "https://example.com", 
                    "author": "Test Author",
                    "sitename": "Test Site",
                    "content_path": "content",
                    "THEME_TEMPLATES_OVERRIDES": "themes/shared"
                },
            }
        )

        # First Run: Initial build using new orchestrator pattern
        original_cwd = os.getcwd()
        try:
            os.chdir(str(temp_filesystem))
            runner = CliRunner()
            result1 = runner.invoke(build)
        finally:
            os.chdir(original_cwd)

        # Assert: Command succeeded and shows expected workflow
        assert result1.exit_code == 0, f"Initial build failed: {result1.output}"
        assert "organization" in result1.output.lower(), (
            "Should show organization cascade"
        )
        assert "generating galleries and site pages" in result1.output.lower(), (
            "Should show orchestrator execution"
        )
        assert "build completed successfully" in result1.output.lower(), (
            "Should show completion message"
        )

        # Assert: Expected directory structure created
        output_dir = temp_filesystem / "output"
        pics_dir = output_dir / "pics" / "full"
        galleries_dir = output_dir / "galleries" / "wedding"

        assert pics_dir.exists(), f"Photos directory not created: {pics_dir}"
        assert galleries_dir.exists(), (
            f"Galleries directory not created: {galleries_dir}"
        )
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
        soup = BeautifulSoup(gallery_html, "html.parser")

        # Should have gallery structure
        assert soup.find("title"), "Gallery should have title"
        assert "wedding" in soup.find("title").text.lower(), (
            "Title should include collection name"
        )

        # Should have image references
        img_elements = soup.find_all("img")
        assert len(img_elements) >= 3, (
            f"Should have 3 images, found {len(img_elements)}"
        )

        # Should have CSS references
        css_links = soup.find_all("link", rel="stylesheet")
        assert len(css_links) >= 1, "Should have CSS stylesheet links"

        # Assert: Galleries and CSS files created by orchestrator
        gallery_files = list(galleries_dir.glob("*"))
        assert len(gallery_files) >= 3, (
            f"Should have multiple gallery files, found {len(gallery_files)}"
        )

        # Verify CSS and thumbnail directory exist (core galleria functionality)
        assert any(f.name.endswith(".css") for f in gallery_files), (
            "Should have CSS files"
        )
        assert (galleries_dir / "thumbnails").exists(), (
            "Should have thumbnails directory"
        )

        # Assert: Pelican site pages generated
        assert (output_dir / "index.html").exists(), "Site index should exist"

        # Parse site index
        index_html = (output_dir / "index.html").read_text()
        index_soup = BeautifulSoup(index_html, "html.parser")
        assert index_soup.find("title"), "Site index should have title"

        # Assert: Build orchestrator completed successfully
        assert (
            "Build completed successfully" in result1.output or "✓" in result1.output
        ), "Should show success"

    def test_build_handles_pelican_file_conflicts_gracefully(
        self, temp_filesystem, full_config_setup, fake_image_factory, directory_factory, file_factory
    ):
        """Test build doesn't fail when Pelican tries to overwrite existing index.html."""

        # Setup: Create source directory with test photos
        fake_image_factory("IMG_001.jpg", directory="source_photos", use_raw_bytes=True)

        # Setup: Create content and theme structure
        setup_shared_theme_structure(directory_factory, file_factory)
        file_factory("content/index.md", """---
title: Test Site
date: 2025-12-02
status: published
slug: index
---

# Test Site Index
This is the main site page.
""")

        # Setup: Configure complete pipeline
        full_config_setup(
            {
                "normpic": {
                    "source_dir": str(temp_filesystem / "source_photos"),
                    "dest_dir": str(temp_filesystem / "output" / "pics" / "full"),
                    "collection_name": "wedding",
                    "collection_description": "Test wedding photos",
                    "create_symlinks": True,
                },
                "galleria": {
                    "manifest_path": str(
                        temp_filesystem / "output" / "pics" / "full" / "manifest.json"
                    ),
                    "output_dir": str(
                        temp_filesystem / "output" / "galleries" / "wedding"
                    ),
                    "thumbnail_size": 400,
                    "photos_per_page": 12,
                    "theme": "minimal",
                    "quality": 85,
                },
                "pelican": {
                    "theme": "themes/site",
                    "site_url": "https://example.com", 
                    "author": "Test Author",
                    "sitename": "Test Site",
                    "content_path": "content",
                    "THEME_TEMPLATES_OVERRIDES": "themes/shared"
                },
            }
        )

        # Act: Run build (should not fail due to file conflicts)
        original_cwd = os.getcwd()
        try:
            os.chdir(str(temp_filesystem))
            runner = CliRunner()
            result = runner.invoke(build)
        finally:
            os.chdir(original_cwd)

        # Assert: Build completes successfully without file overwrite errors
        assert result.exit_code == 0, f"Build failed with conflict: {result.output}"
        assert "is to be overwritten" not in result.output, "Should not have overwrite conflicts"
        assert "build completed successfully" in result.output.lower(), "Should complete successfully"

        # Assert: Final index.html contains Pelican content, not conflicting content
        index_html = (temp_filesystem / "output" / "index.html").read_text()
        assert "Test Site Index" in index_html, "Should contain Pelican-generated content"
