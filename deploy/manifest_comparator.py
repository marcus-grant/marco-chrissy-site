"""Manifest comparison logic for incremental deploy operations."""

import hashlib
from pathlib import Path


class ManifestComparator:
    """Compare local and remote manifests to determine incremental upload requirements."""

    def __init__(self):
        """Initialize manifest comparator."""
        pass

    def generate_local_manifest(self, directory: Path) -> dict[str, str]:
        """Generate manifest of local files with their hashes.

        Args:
            directory: Directory to scan for files

        Returns:
            Dictionary mapping file paths to their SHA-256 hashes
        """
        manifest = {}

        try:
            for file_path in directory.rglob("*"):
                if file_path.is_file() and file_path.name != "manifest.json":
                    # Use relative path from the directory as key
                    relative_path = file_path.relative_to(directory)
                    manifest[str(relative_path)] = self.calculate_file_hash(file_path)

            return manifest

        except Exception:
            return {}

    def compare_manifests(self, local_manifest: dict[str, str], remote_manifest: dict[str, str]) -> set[str]:
        """Compare local and remote manifests to find files needing upload.

        Args:
            local_manifest: Local file path to hash mapping
            remote_manifest: Remote file path to hash mapping

        Returns:
            Set of file paths that need to be uploaded (new or changed files)
        """
        files_to_upload = set()

        for file_path, local_hash in local_manifest.items():
            remote_hash = remote_manifest.get(file_path)

            # Upload if file is new (not in remote) or changed (different hash)
            if remote_hash is None or remote_hash != local_hash:
                files_to_upload.add(file_path)

        return files_to_upload

    def load_manifest_from_json(self, manifest_content: bytes) -> dict[str, str]:
        """Load manifest from JSON bytes (downloaded from remote).

        Args:
            manifest_content: JSON manifest content as bytes

        Returns:
            Dictionary mapping file paths to their hashes
        """
        # Stub implementation - will be implemented in TDD cycle
        raise NotImplementedError("JSON manifest loading not implemented yet")

    def save_manifest_to_json(self, manifest: dict[str, str]) -> bytes:
        """Save manifest to JSON bytes for upload.

        Args:
            manifest: Dictionary mapping file paths to their hashes

        Returns:
            JSON manifest content as bytes
        """
        # Stub implementation - will be implemented in TDD cycle
        raise NotImplementedError("JSON manifest saving not implemented yet")

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file.

        Args:
            file_path: Path to file to hash

        Returns:
            SHA-256 hash as hex string
        """
        hash_algo = hashlib.sha256()

        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_algo.update(chunk)
            return hash_algo.hexdigest()

        except Exception:
            # Return empty hash for files that cannot be read
            return ""
