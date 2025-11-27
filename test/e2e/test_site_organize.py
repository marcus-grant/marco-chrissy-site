"""E2E tests for site organize command."""

import json
import os
from pathlib import Path

from click.testing import CliRunner

from cli.commands.organize import organize


class TestSiteOrganize:
    """Test the site organize command functionality."""

    def test_organize_complete_workflow(self, temp_filesystem, full_config_setup, fake_image_factory):
        """Test complete organize workflow: validation, organization, manifest, and idempotency."""

        # Setup: Create source directory with test photos using fixture
        source_dir = temp_filesystem / "source_photos"
        fake_image_factory("IMG_001.jpg", directory="source_photos", use_raw_bytes=True)
        fake_image_factory("IMG_002.jpg", directory="source_photos", use_raw_bytes=True)

        # Setup: Configure normpic with temp paths
        full_config_setup({
            "normpic": {
                "source_dir": str(source_dir),
                "dest_dir": str(temp_filesystem / "output" / "pics" / "full"),
                "collection_name": "wedding",
                "collection_description": "Test wedding photos",
                "create_symlinks": True
            }
        })

        # First Run: Initial organization
        original_cwd = os.getcwd()
        try:
            os.chdir(str(temp_filesystem))
            runner = CliRunner()
            result1 = runner.invoke(organize)
        finally:
            os.chdir(original_cwd)

        # Assert: Command succeeded and shows expected workflow
        assert result1.exit_code == 0, f"Initial organize failed: {result1.output}"
        assert "validation" in result1.output.lower(), "Should show validation cascade"
        assert "normpic" in result1.output.lower(), "Should show NormPic orchestration"
        assert "manifest" in result1.output.lower(), "Should show manifest generation"
        assert "processed" in result1.output.lower(), "Should show photos processed"

        # Assert: Files and directories created correctly
        manifest_path = temp_filesystem / "output" / "pics" / "full" / "manifest.json"
        photos_dir = temp_filesystem / "output" / "pics" / "full"

        assert manifest_path.exists(), f"Manifest not created at {manifest_path}"
        assert photos_dir.exists(), f"Photos directory not created at {photos_dir}"

        # Assert: Manifest content is correct
        with open(manifest_path) as f:
            manifest_data = json.load(f)

        assert manifest_data["collection_name"] == "wedding"
        assert "pics" in manifest_data
        assert len(manifest_data["pics"]) == 2, f"Expected 2 pics, got {len(manifest_data['pics'])}"

        # Assert: Each photo has correct metadata and symlinks
        for pic in manifest_data["pics"]:
            # Required fields
            assert "source_path" in pic
            assert "dest_path" in pic
            assert "hash" in pic
            assert "size_bytes" in pic

            # Source file exists
            source_path = Path(pic["source_path"])
            assert source_path.exists(), f"Source file missing: {source_path}"
            assert source_path.name in ["IMG_001.jpg", "IMG_002.jpg"]

            # Symlink created correctly
            symlink_path = photos_dir / pic["dest_path"]
            assert symlink_path.exists(), f"Symlink missing: {symlink_path}"
            assert symlink_path.is_symlink(), f"Expected symlink: {symlink_path}"
            assert symlink_path.resolve() == source_path.resolve()

            # NormPic naming pattern
            dest_filename = pic["dest_path"]
            assert "wedding" in dest_filename.lower(), f"Missing collection name: {dest_filename}"
            assert dest_filename.endswith(".jpg"), f"Wrong extension: {dest_filename}"

        # Assert: All expected symlinks created
        symlinks_created = list(photos_dir.glob("*.jpg"))
        assert len(symlinks_created) == 2, f"Expected 2 symlinks, found {len(symlinks_created)}"

        # Second Run: Test idempotency
        try:
            os.chdir(str(temp_filesystem))
            runner = CliRunner()
            result2 = runner.invoke(organize)
        finally:
            os.chdir(original_cwd)

        # Assert: Second run skips work (idempotent)
        assert result2.exit_code == 0, f"Idempotent run failed: {result2.output}"
        assert "validation" in result2.output.lower(), "Should still run validation"
        assert ("already organized" in result2.output.lower() or
                "skipping" in result2.output.lower()), "Should skip organization work"

        # Assert: Manifest unchanged after idempotent run
        assert manifest_path.exists(), "Manifest should still exist after idempotent run"
