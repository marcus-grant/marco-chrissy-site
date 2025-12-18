"""E2E test to verify shared navbar appears in both Pelican and Galleria pages."""

import json


def test_shared_navbar_appears_in_both_systems(temp_filesystem, full_config_setup, file_factory, directory_factory):
    """Verify shared navbar HTML appears in both Pelican and Galleria generated pages.

    This is the actual integration test that verifies shared components work:
    1. Mock shared navbar component with recognizable HTML
    2. Build both Pelican and Galleria
    3. Check generated HTML files contain the shared navbar
    """
    # Create shared navbar component with clear test ID
    directory_factory("themes/shared/templates")
    file_factory(
        "themes/shared/templates/navbar.html",
        '<nav id="test-shared-navbar"><a href="/">Home</a><a href="/about/">About</a><a href="/galleries/wedding/">Gallery</a></nav>'
    )

    # Create minimal base template that includes CSS_FILE
    file_factory(
        "themes/shared/templates/base.html",
        """<!DOCTYPE html>
<html><head><title>{{ SITENAME }}</title>
{% if CSS_FILE %}<link rel="stylesheet" href="{{ SITEURL }}/{{ THEME_STATIC_DIR }}/css/{{ CSS_FILE }}" />{% endif %}
</head><body>{% block content %}Content goes here{% endblock %}</body></html>"""
    )

    file_factory("themes/shared/templates/article.html", """{% extends "base.html" %}
{% block content %}{{ article.content }}{% endblock %}""")
    file_factory("themes/shared/templates/index.html", """{% extends "base.html" %}
{% block content %}{% for article in articles %}{{ article.content }}{% endfor %}{% endblock %}""")

    # Create shared CSS with vibrant ugly color for easy detection
    directory_factory("themes/shared/static/css")
    file_factory(
        "themes/shared/static/css/shared.css",
        '.test-shared-nav { background: #ff00ff; color: #00ff00; font-size: 24px; }'
    )

    # Create minimal content for Pelican that includes shared navbar
    file_factory("content/index.md", """Title: Home
Date: 2023-01-01

# Home Page
{% include 'navbar.html' %}
This is the home page.
""")

    # Create test photo manifest for Galleria
    directory_factory("output/pics/full")
    file_factory("output/pics/full/manifest.json", """{
    "version": "0.1.0",
    "collection_name": "test_wedding",
    "pics": [
        {
            "source_path": "/fake/photo.jpg",
            "dest_path": "photo.jpg",
            "hash": "abc123",
            "size_bytes": 1024,
            "mtime": 1234567890
        }
    ]
}""")

    # Configure both systems to use shared components
    configs = full_config_setup({
        "pelican": {
            "author": "Test",
            "sitename": "Test Site",
            "content_path": "content",
            "SHARED_THEME_PATH": "themes/shared"
        },
        "galleria": {
            "manifest_path": "output/pics/full/manifest.json",
            "output_dir": "output/galleries/wedding",
            "theme": "minimal",
            "SHARED_THEME_PATH": "themes/shared"
        }
    })

    # Test Pelican build directly
    from build.pelican_builder import PelicanBuilder

    with open(configs["pelican"]) as f:
        pelican_config = json.load(f)

    pelican_builder = PelicanBuilder()
    pelican_result = pelican_builder.build({"output_dir": "output"}, pelican_config, temp_filesystem)
    assert pelican_result, "Pelican build failed"

    # Test Galleria build directly
    from build.galleria_builder import GalleriaBuilder

    with open(configs["galleria"]) as f:
        galleria_config = json.load(f)

    galleria_builder = GalleriaBuilder()
    galleria_result = galleria_builder.build(galleria_config, temp_filesystem)
    assert galleria_result, "Galleria build failed"

    # Check Pelican output contains shared navbar
    pelican_index = temp_filesystem / "output" / "index.html"
    assert pelican_index.exists(), "Pelican index.html not generated"
    pelican_content = pelican_index.read_text()
    assert 'id="test-shared-navbar"' in pelican_content, "Shared navbar missing from Pelican page"

    # Check Pelican output contains shared CSS file
    pelican_css = temp_filesystem / "output" / "theme" / "css" / "shared.css"
    assert pelican_css.exists(), f"Shared CSS file missing from Pelican output at {pelican_css}"
    pelican_css_content = pelican_css.read_text()
    assert 'background: #ff00ff' in pelican_css_content, "Shared CSS with ugly color missing from Pelican output"

    # Check Pelican HTML links to shared CSS
    assert 'shared.css' in pelican_content, "Pelican HTML should reference shared CSS file"

    # Check Galleria output contains shared navbar
    galleria_page = temp_filesystem / "output" / "galleries" / "wedding" / "page_1.html"
    assert galleria_page.exists(), "Galleria page_1.html not generated"
    galleria_content = galleria_page.read_text()
    assert 'id="test-shared-navbar"' in galleria_content, "Shared navbar missing from Galleria page"

    # Check Galleria output contains shared CSS file
    galleria_css = temp_filesystem / "output" / "galleries" / "wedding" / "shared.css"
    assert galleria_css.exists(), f"Shared CSS file missing from Galleria output at {galleria_css}"
    galleria_css_content = galleria_css.read_text()
    assert 'background: #ff00ff' in galleria_css_content, "Shared CSS with ugly color missing from Galleria output"

    # Check Galleria HTML links to shared CSS
    assert 'shared.css' in galleria_content, "Galleria HTML should reference shared CSS file"

    # Verify both have the same navigation links
    for content in [pelican_content, galleria_content]:
        assert '<a href="/">Home</a>' in content, "Home link missing from navbar"
        assert '<a href="/about/">About</a>' in content, "About link missing from navbar"
        assert '<a href="/galleries/wedding/">Gallery</a>' in content, "Gallery link missing from navbar"
