"""Basic unit tests for PipelineManager - just initialization."""

import pytest


class TestPipelineManagerBasic:
    """Basic tests for PipelineManager initialization."""

    def test_pipeline_manager_can_be_created(self):
        """Test PipelineManager can be instantiated."""
        # This will fail - PipelineManager doesn't exist yet
        from galleria.manager.pipeline import PipelineManager
        
        manager = PipelineManager()
        assert manager is not None