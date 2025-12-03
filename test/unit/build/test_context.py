"""Unit tests for BuildContext class."""

import pytest

from build.context import BuildContext


class TestBuildContext:
    """Test BuildContext class functionality."""

    def test_build_context_production_true(self):
        """Test BuildContext with production=True."""
        context = BuildContext(production=True)
        assert context.production is True

    def test_build_context_production_false(self):
        """Test BuildContext with production=False for development."""
        context = BuildContext(production=False)
        assert context.production is False

    def test_build_context_default_production_true(self):
        """Test BuildContext defaults to production=True."""
        context = BuildContext()
        assert context.production is True