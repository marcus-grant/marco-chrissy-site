"""E2E tests for site organize command."""

import json
import os
import subprocess
import pytest
from pathlib import Path


class TestSiteOrganize:
    """Test the site organize command functionality."""

    def test_organize_calls_normpic(self, temp_filesystem, full_config_setup):
        """Test that organize command orchestrates NormPic."""
        full_config_setup()
        
        result = subprocess.run(
            ["uv", "run", "site", "organize"],
            capture_output=True,
            text=True,
            cwd=str(temp_filesystem)
        )
        assert result.returncode == 0
        assert "normpic" in result.stdout.lower()

    def test_organize_generates_manifest(self, temp_filesystem, full_config_setup, file_factory):
        """Test that organize command generates photo manifest."""
        # Create source directory with test photos
        source_dir = temp_filesystem / "source_photos"
        source_dir.mkdir(parents=True, exist_ok=True)
        
        # Create fake JPEG files with minimal JPEG structure and fake EXIF
        fake_jpeg_with_exif = (
            b'\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
            b'\xff\xe1\x00\x16Exif\x00\x00II*\x00\x08\x00\x00\x00'  # Fake EXIF header
            b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f'
            b'\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01'
            b'\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08'
            b'\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xd2\xcf \xff\xd9'  # End of Image
        )
        
        # Create test image files with fake JPEG structure
        (source_dir / "IMG_001.jpg").write_bytes(fake_jpeg_with_exif)
        (source_dir / "IMG_002.jpg").write_bytes(fake_jpeg_with_exif)
        
        # Set up configs with custom normpic config pointing to our temp paths
        configs = full_config_setup({
            "normpic": {
                "source_dir": str(source_dir),
                "dest_dir": str(temp_filesystem / "output" / "pics" / "full"),
                "collection_name": "wedding",
                "collection_description": "Test wedding photos",
                "create_symlinks": True
            }
        })
        
        # Run organize command from temp filesystem directory
        result = subprocess.run(
            ["uv", "run", "site", "organize"],
            capture_output=True,
            text=True,
            cwd=str(temp_filesystem)
        )
        
        # Verify command success
        assert result.returncode == 0, f"Command failed: {result.stderr}\nStdout: {result.stdout}"
        assert "manifest" in result.stdout.lower()
        assert "processed" in result.stdout.lower()
        
        # Verify manifest file was created
        manifest_path = temp_filesystem / "output" / "pics" / "full" / "manifest.json"
        assert manifest_path.exists(), f"Manifest not found at {manifest_path}"
        
        # Verify organized photos directory exists
        photos_dir = temp_filesystem / "output" / "pics" / "full"
        assert photos_dir.exists(), f"Photos directory not found at {photos_dir}"
        
        # Parse and verify manifest content
        with open(manifest_path) as f:
            manifest_data = json.load(f)
        
        assert "collection_name" in manifest_data
        assert manifest_data["collection_name"] == "wedding"
        assert "pics" in manifest_data
        assert len(manifest_data["pics"]) == 2, f"Expected 2 pics, got {len(manifest_data['pics'])}"
        
        # Verify each photo entry in manifest
        for pic in manifest_data["pics"]:
            assert "source_path" in pic
            assert "dest_path" in pic
            assert "hash" in pic
            assert "size_bytes" in pic
            
            # Verify source path points to our test files
            source_path = Path(pic["source_path"])
            assert source_path.exists(), f"Source file doesn't exist: {source_path}"
            assert source_path.name in ["IMG_001.jpg", "IMG_002.jpg"]
            
            # Verify symlink was created with NormPic naming pattern
            symlink_path = photos_dir / pic["dest_path"]
            assert symlink_path.exists(), f"Symlink doesn't exist: {symlink_path}"
            assert symlink_path.is_symlink(), f"Expected symlink, got regular file: {symlink_path}"
            
            # Verify symlink points to correct source
            assert symlink_path.resolve() == source_path.resolve(), f"Symlink points to wrong file: {symlink_path} -> {symlink_path.resolve()}, expected {source_path}"
            
            # Verify NormPic filename pattern (should contain collection name and timestamp)
            dest_filename = pic["dest_path"]
            assert "wedding" in dest_filename.lower(), f"Collection name not in filename: {dest_filename}"
            assert dest_filename.endswith(".jpg"), f"Wrong file extension: {dest_filename}"
        
        # Verify all symlinks are accounted for
        symlinks_created = list(photos_dir.glob("*.jpg"))
        assert len(symlinks_created) == 2, f"Expected 2 symlinks, found {len(symlinks_created)}: {[s.name for s in symlinks_created]}"

    @pytest.mark.skip(reason="Organize command functionality not yet implemented")
    def test_organize_calls_validate_automatically(self):
        """Test that organize automatically calls validate if needed."""
        result = subprocess.run(
            ["uv", "run", "site", "organize"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        # Should see evidence that validate was called
        assert "validate" in result.stdout.lower()

    @pytest.mark.skip(reason="Organize command functionality not yet implemented")
    def test_organize_is_idempotent(self):
        """Test that organize skips work if already done."""
        # Run twice, second should be faster/skip work
        pass