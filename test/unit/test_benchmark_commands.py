"""Unit tests for benchmark flags on CLI commands."""

import os

from click.testing import CliRunner


class TestValidateBenchmarkFlag:
    """Test --benchmark flag on validate command."""

    def test_validate_with_benchmark_returns_timing(
        self, temp_filesystem, full_config_setup
    ):
        """Test validate --benchmark outputs timing information."""
        from cli.commands.validate import validate

        full_config_setup()

        original_cwd = os.getcwd()
        try:
            os.chdir(str(temp_filesystem))
            runner = CliRunner()
            result = runner.invoke(validate, ["--benchmark"])
        finally:
            os.chdir(original_cwd)

        assert result.exit_code == 0
        assert "duration" in result.output.lower() or "seconds" in result.output.lower()

    def test_validate_without_benchmark_no_timing(
        self, temp_filesystem, full_config_setup
    ):
        """Test validate without --benchmark does not output timing."""
        from cli.commands.validate import validate

        full_config_setup()

        original_cwd = os.getcwd()
        try:
            os.chdir(str(temp_filesystem))
            runner = CliRunner()
            result = runner.invoke(validate)
        finally:
            os.chdir(original_cwd)

        assert result.exit_code == 0
        # Should not have timing output unless benchmark flag is set
        assert "duration" not in result.output.lower()


class TestOrganizeBenchmarkFlag:
    """Test --benchmark flag on organize command."""

    def test_organize_with_benchmark_returns_timing(
        self, temp_filesystem, full_config_setup, fake_image_factory
    ):
        """Test organize --benchmark outputs timing information."""
        from cli.commands.organize import organize

        fake_image_factory("IMG_001.jpg", directory="source_photos", use_raw_bytes=True)
        full_config_setup(
            {
                "normpic": {
                    "source_dir": str(temp_filesystem / "source_photos"),
                    "dest_dir": str(temp_filesystem / "output" / "pics" / "full"),
                    "collection_name": "test",
                    "collection_description": "Test",
                    "create_symlinks": True,
                }
            }
        )

        original_cwd = os.getcwd()
        try:
            os.chdir(str(temp_filesystem))
            runner = CliRunner()
            result = runner.invoke(organize, ["--benchmark"])
        finally:
            os.chdir(original_cwd)

        assert result.exit_code == 0
        assert "duration" in result.output.lower() or "seconds" in result.output.lower()


class TestBuildBenchmarkFlag:
    """Test --benchmark flag on build command."""

    def test_build_with_benchmark_returns_timing(
        self,
        temp_filesystem,
        full_config_setup,
        fake_image_factory,
        directory_factory,
        file_factory,
    ):
        """Test build --benchmark outputs timing information."""
        from cli.commands.build import build

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
                    "collection_name": "test",
                    "collection_description": "Test",
                    "create_symlinks": True,
                },
                "galleria": {
                    "manifest_path": str(
                        temp_filesystem / "output" / "pics" / "full" / "manifest.json"
                    ),
                    "output_dir": str(
                        temp_filesystem / "output" / "galleries" / "test"
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

        original_cwd = os.getcwd()
        try:
            os.chdir(str(temp_filesystem))
            runner = CliRunner()
            result = runner.invoke(build, ["--benchmark"])
        finally:
            os.chdir(original_cwd)

        assert result.exit_code == 0
        assert "duration" in result.output.lower() or "seconds" in result.output.lower()
