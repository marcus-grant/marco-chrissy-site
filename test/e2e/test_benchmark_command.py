"""E2E tests for site benchmark command."""

import json
import os

import pytest
from click.testing import CliRunner


class TestSiteBenchmark:
    """Test the site benchmark command functionality."""

    def test_benchmark_runs_full_pipeline_with_instrumentation(
        self,
        temp_filesystem,
        full_config_setup,
        fake_image_factory,
        directory_factory,
        file_factory,
    ):
        """Test site benchmark runs full pipeline and collects metrics."""
        from cli.commands.benchmark import benchmark

        # Setup: Create source directory with test photos
        fake_image_factory("IMG_001.jpg", directory="source_photos", use_raw_bytes=True)
        fake_image_factory("IMG_002.jpg", directory="source_photos", use_raw_bytes=True)
        fake_image_factory("IMG_003.jpg", directory="source_photos", use_raw_bytes=True)

        # Setup: Create content and theme structure
        directory_factory("content")
        directory_factory("themes/site/templates")
        directory_factory("themes/shared/templates")

        file_factory(
            "themes/shared/templates/navbar.html",
            '<nav id="test-navbar"><a href="/">Home</a></nav>',
        )
        file_factory(
            "themes/site/templates/base.html",
            """<!DOCTYPE html>
<html><head><title>{{ SITENAME }}</title></head>
<body>{% include 'navbar.html' %}{% block content %}{% endblock %}</body>
</html>""",
        )
        file_factory(
            "themes/site/templates/index.html",
            '{% extends "base.html" %}{% block content %}Index{% endblock %}',
        )

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
                    "THEME_TEMPLATES_OVERRIDES": "themes/shared",
                },
            }
        )

        # Create .benchmarks directory
        benchmarks_dir = temp_filesystem / ".benchmarks"
        benchmarks_dir.mkdir(exist_ok=True)

        # Act: Run benchmark command
        original_cwd = os.getcwd()
        try:
            os.chdir(str(temp_filesystem))
            runner = CliRunner()
            result = runner.invoke(benchmark)
        finally:
            os.chdir(original_cwd)

        # Assert: Command succeeded
        assert result.exit_code == 0, f"Benchmark failed: {result.output}"

    def test_benchmark_outputs_to_benchmarks_directory(
        self,
        temp_filesystem,
        full_config_setup,
        fake_image_factory,
        directory_factory,
        file_factory,
    ):
        """Test site benchmark outputs results to /.benchmarks/ directory."""
        from cli.commands.benchmark import benchmark

        # Setup: Minimal config for speed
        fake_image_factory("IMG_001.jpg", directory="source_photos", use_raw_bytes=True)

        directory_factory("content")
        directory_factory("themes/site/templates")
        directory_factory("themes/shared/templates")

        file_factory("themes/shared/templates/navbar.html", "<nav></nav>")
        file_factory(
            "themes/site/templates/base.html",
            "<html><body>{% block content %}{% endblock %}</body></html>",
        )
        file_factory(
            "themes/site/templates/index.html",
            '{% extends "base.html" %}{% block content %}{% endblock %}',
        )

        full_config_setup(
            {
                "normpic": {
                    "source_dir": str(temp_filesystem / "source_photos"),
                    "dest_dir": str(temp_filesystem / "output" / "pics" / "full"),
                    "collection_name": "wedding",
                    "collection_description": "Test",
                    "create_symlinks": True,
                },
                "galleria": {
                    "manifest_path": str(
                        temp_filesystem / "output" / "pics" / "full" / "manifest.json"
                    ),
                    "output_dir": str(
                        temp_filesystem / "output" / "galleries" / "wedding"
                    ),
                    "thumbnail_size": 200,
                    "photos_per_page": 12,
                    "theme": "minimal",
                    "quality": 85,
                },
                "pelican": {
                    "theme": "themes/site",
                    "site_url": "https://example.com",
                    "author": "Test",
                    "sitename": "Test",
                    "content_path": "content",
                    "THEME_TEMPLATES_OVERRIDES": "themes/shared",
                },
            }
        )

        # Act: Run benchmark command
        original_cwd = os.getcwd()
        try:
            os.chdir(str(temp_filesystem))
            runner = CliRunner()
            result = runner.invoke(benchmark)
        finally:
            os.chdir(original_cwd)

        # Assert: Output file exists in .benchmarks
        assert result.exit_code == 0, f"Benchmark failed: {result.output}"

        benchmarks_dir = temp_filesystem / ".benchmarks"
        assert benchmarks_dir.exists(), "/.benchmarks/ directory should exist"

        benchmark_files = list(benchmarks_dir.glob("*.json"))
        assert len(benchmark_files) >= 1, "Should have at least one benchmark result file"

    def test_benchmark_output_includes_stage_metrics(
        self,
        temp_filesystem,
        full_config_setup,
        fake_image_factory,
        directory_factory,
        file_factory,
    ):
        """Test benchmark output includes metrics from validate, organize, build stages."""
        from cli.commands.benchmark import benchmark

        # Setup: Minimal config
        fake_image_factory("IMG_001.jpg", directory="source_photos", use_raw_bytes=True)

        directory_factory("content")
        directory_factory("themes/site/templates")
        directory_factory("themes/shared/templates")

        file_factory("themes/shared/templates/navbar.html", "<nav></nav>")
        file_factory(
            "themes/site/templates/base.html",
            "<html><body>{% block content %}{% endblock %}</body></html>",
        )
        file_factory(
            "themes/site/templates/index.html",
            '{% extends "base.html" %}{% block content %}{% endblock %}',
        )

        full_config_setup(
            {
                "normpic": {
                    "source_dir": str(temp_filesystem / "source_photos"),
                    "dest_dir": str(temp_filesystem / "output" / "pics" / "full"),
                    "collection_name": "wedding",
                    "collection_description": "Test",
                    "create_symlinks": True,
                },
                "galleria": {
                    "manifest_path": str(
                        temp_filesystem / "output" / "pics" / "full" / "manifest.json"
                    ),
                    "output_dir": str(
                        temp_filesystem / "output" / "galleries" / "wedding"
                    ),
                    "thumbnail_size": 200,
                    "photos_per_page": 12,
                    "theme": "minimal",
                    "quality": 85,
                },
                "pelican": {
                    "theme": "themes/site",
                    "site_url": "https://example.com",
                    "author": "Test",
                    "sitename": "Test",
                    "content_path": "content",
                    "THEME_TEMPLATES_OVERRIDES": "themes/shared",
                },
            }
        )

        # Act: Run benchmark command
        original_cwd = os.getcwd()
        try:
            os.chdir(str(temp_filesystem))
            runner = CliRunner()
            result = runner.invoke(benchmark)
        finally:
            os.chdir(original_cwd)

        # Assert: Benchmark output contains stage metrics
        assert result.exit_code == 0, f"Benchmark failed: {result.output}"

        benchmarks_dir = temp_filesystem / ".benchmarks"
        benchmark_files = list(benchmarks_dir.glob("*.json"))
        assert len(benchmark_files) >= 1, "Should have benchmark result file"

        # Load and validate the benchmark result
        with open(benchmark_files[0]) as f:
            benchmark_data = json.load(f)

        # Check for required metric sections
        assert "metadata" in benchmark_data, "Should have metadata section"
        assert "build_metrics" in benchmark_data, "Should have build_metrics section"

        build_metrics = benchmark_data["build_metrics"]
        assert "validate_duration_s" in build_metrics, "Should have validate timing"
        assert "organize_duration_s" in build_metrics, "Should have organize timing"
        assert "build_duration_s" in build_metrics, "Should have build timing"
