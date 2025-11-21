"""Unit tests for NormPic integration functionality."""

import pytest
from organizer.normpic import NormPicOrganizer, OrganizeResult


class TestNormPicOrganizer:
    """Test NormPic orchestration functionality."""

    def test_organizer_initialization(self):
        """Test that NormPicOrganizer can be initialized."""
        organizer = NormPicOrganizer()
        assert organizer is not None

    def test_organize_photos_returns_result(self):
        """Test that organize_photos returns an OrganizeResult."""
        organizer = NormPicOrganizer()
        result = organizer.organize_photos()
        
        assert isinstance(result, OrganizeResult)
        assert hasattr(result, 'success')
        assert hasattr(result, 'errors')

    def test_organize_result_dataclass(self):
        """Test OrganizeResult dataclass creation."""
        result = OrganizeResult(success=True, errors=[])
        assert result.success is True
        assert result.errors == []
        
        result_with_errors = OrganizeResult(success=False, errors=["test error"])
        assert result_with_errors.success is False
        assert result_with_errors.errors == ["test error"]