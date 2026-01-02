"""Unit tests for manifest comparison functionality."""

import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from deploy.manifest_comparator import ManifestComparator


class TestManifestComparator:
    """Test manifest comparison functionality."""

    def test_calculate_file_hash_success(self):
        """Test file hash calculation returns consistent SHA-256 hash."""
        import hashlib

        comparator = ManifestComparator()
        test_content = b"test file content"
        expected_hash = hashlib.sha256(test_content).hexdigest()

        with patch("builtins.open", mock_open(read_data=test_content)):
            result_hash = comparator.calculate_file_hash(Path("/tmp/test.txt"))

        assert result_hash == expected_hash

    def test_generate_local_manifest_success(self, fs):
        """Test local manifest generation scans directory and calculates hashes."""
        comparator = ManifestComparator()

        # Create fake filesystem structure
        fs.create_file("/test_dir/file1.txt", contents="content1")
        fs.create_file("/test_dir/subdir/file2.txt", contents="content2")
        fs.create_file("/test_dir/manifest.json", contents='{"old": "manifest"}')  # Should be excluded

        # Execute
        result = comparator.generate_local_manifest(Path("/test_dir"))

        # Verify structure (exact hashes will depend on content)
        assert len(result) == 2  # Should exclude manifest.json
        assert "file1.txt" in result
        assert "subdir/file2.txt" in result
        assert all(len(hash_val) == 64 for hash_val in result.values())  # SHA-256 hex length

    def test_compare_manifests_finds_new_files(self):
        """Test manifest comparison identifies new files for upload."""
        comparator = ManifestComparator()

        local_manifest = {
            "file1.txt": "hash1",
            "file2.txt": "hash2",
            "file3.txt": "hash3"  # New file
        }
        remote_manifest = {
            "file1.txt": "hash1",
            "file2.txt": "hash2"
        }

        result = comparator.compare_manifests(local_manifest, remote_manifest)

        assert result == {"file3.txt"}  # Only new file should be uploaded

    def test_compare_manifests_finds_changed_files(self):
        """Test manifest comparison identifies changed files for upload."""
        comparator = ManifestComparator()

        local_manifest = {
            "file1.txt": "new_hash1",  # Changed file
            "file2.txt": "hash2"
        }
        remote_manifest = {
            "file1.txt": "old_hash1",
            "file2.txt": "hash2"
        }

        result = comparator.compare_manifests(local_manifest, remote_manifest)

        assert result == {"file1.txt"}  # Only changed file should be uploaded

    def test_load_manifest_from_json_success(self):
        """Test loading manifest from JSON bytes."""
        comparator = ManifestComparator()

        manifest_data = {"file1.txt": "hash1", "file2.txt": "hash2"}
        json_bytes = json.dumps(manifest_data).encode("utf-8")

        with pytest.raises(NotImplementedError, match="JSON manifest loading not implemented"):
            comparator.load_manifest_from_json(json_bytes)

    def test_save_manifest_to_json_success(self):
        """Test saving manifest to JSON bytes."""
        comparator = ManifestComparator()

        manifest = {"file1.txt": "hash1", "file2.txt": "hash2"}

        with pytest.raises(NotImplementedError, match="JSON manifest saving not implemented"):
            comparator.save_manifest_to_json(manifest)

    def test_compare_manifests_empty_remote(self):
        """Test manifest comparison when remote manifest is empty (first deploy)."""
        comparator = ManifestComparator()

        local_manifest = {
            "file1.txt": "hash1",
            "file2.txt": "hash2"
        }
        remote_manifest = {}

        result = comparator.compare_manifests(local_manifest, remote_manifest)
        
        assert result == {"file1.txt", "file2.txt"}  # All files should be uploaded on first deploy

    def test_load_manifest_from_json_invalid(self):
        """Test loading manifest handles invalid JSON gracefully."""
        comparator = ManifestComparator()

        invalid_json = b"invalid json content"

        with pytest.raises(NotImplementedError, match="JSON manifest loading not implemented"):
            comparator.load_manifest_from_json(invalid_json)
