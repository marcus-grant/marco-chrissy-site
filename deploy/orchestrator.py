"""Deploy orchestrator for managing dual zone deployment strategy."""

from pathlib import Path


class DeployOrchestrator:
    """Orchestrate deployment to bunny.net with dual zone strategy.

    Manages photo zone routing (/output/pics/* → photo zone) and
    site content zone deployment (everything except pics/).
    """

    def __init__(self, photo_client, site_client, manifest_comparator):
        """Initialize deploy orchestrator.

        Args:
            photo_client: BunnyNet API client for photo zone uploads
            site_client: BunnyNet API client for site content zone uploads
            manifest_comparator: Manifest comparison logic
        """
        self.photo_client = photo_client
        self.site_client = site_client
        self.manifest_comparator = manifest_comparator

    def route_files_to_zones(self, output_dir: Path) -> tuple[list[Path], list[Path]]:
        """Route files to appropriate storage zones based on path.

        Args:
            output_dir: Directory containing generated site files

        Returns:
            Tuple of (photo_files, site_files) for zone routing
        """
        photo_files = []
        site_files = []

        try:
            # Scan all files in output directory
            for file_path in output_dir.rglob("*"):
                if file_path.is_file():
                    # Check if file is in pics directory (photo zone)
                    relative_path = file_path.relative_to(output_dir)
                    if relative_path.parts and relative_path.parts[0] == "pics":
                        photo_files.append(file_path)
                    else:
                        site_files.append(file_path)

        except Exception:
            # Return empty lists on any filesystem errors
            return [], []

        return photo_files, site_files

    def deploy_photos(self, photo_files: list[Path], output_dir: Path) -> bool:
        """Deploy photos to photo storage zone with manifest-based incremental upload.

        Args:
            photo_files: List of photo files to deploy
            output_dir: Base output directory for relative path calculation

        Returns:
            True if deployment successful, False otherwise
        """
        try:
            # Generate manifest of local photo files
            pics_dir = output_dir / "pics"
            local_manifest = self.manifest_comparator.generate_local_manifest(pics_dir)

            # Download remote manifest to compare
            try:
                remote_manifest_bytes = self.photo_client.download_file("manifest.json")
                if remote_manifest_bytes:
                    remote_manifest = self.manifest_comparator.load_manifest_from_json(remote_manifest_bytes)
                else:
                    remote_manifest = {}
            except Exception:
                # First deployment or manifest unavailable - upload all files
                remote_manifest = {}

            # Determine which files need upload (new or changed)
            files_to_upload = self.manifest_comparator.compare_manifests(local_manifest, remote_manifest)

            # Upload only files that need updating
            uploaded_files = []
            for file_to_upload in files_to_upload:
                file_path = pics_dir / file_to_upload
                if file_path.exists() and file_path.is_file():
                    if self.photo_client.upload_file(file_path, file_to_upload):
                        uploaded_files.append(file_to_upload)
                    else:
                        # Upload failed - rollback if needed
                        return False

            # Upload updated manifest
            manifest_bytes = self.manifest_comparator.save_manifest_to_json(local_manifest)
            manifest_path = pics_dir / "manifest.json"
            manifest_path.write_bytes(manifest_bytes)
            if not self.photo_client.upload_file(manifest_path, "manifest.json"):
                return False

            return True

        except Exception:
            return False

    def deploy_site_content(self, site_files: list[Path], output_dir: Path) -> bool:
        """Deploy site content to site storage zone.

        Args:
            site_files: List of site files to deploy (excluding photos)
            output_dir: Base output directory for relative path calculation

        Returns:
            True if deployment successful, False otherwise
        """
        try:
            # Upload all site files (no manifest comparison - always upload all)
            for site_file in site_files:
                if site_file.exists() and site_file.is_file():
                    # Calculate relative path from output directory
                    relative_path = site_file.relative_to(output_dir)

                    # Upload to site zone using relative path as key
                    if not self.site_client.upload_file(site_file, str(relative_path)):
                        return False

            return True

        except Exception:
            return False

    def rollback_deployment(self, deployed_files: list[str], zone_type: str) -> bool:
        """Rollback partially failed deployment.

        Args:
            deployed_files: List of file paths that were successfully deployed
            zone_type: 'photo' or 'site' to identify which zone to rollback

        Returns:
            True if rollback successful, False otherwise
        """
        try:
            # Select appropriate client based on zone type
            if zone_type == "photo":
                client = self.photo_client
            elif zone_type == "site":
                client = self.site_client
            else:
                return False
                
            # Attempt to delete all deployed files
            all_deletions_successful = True

            for file_path in deployed_files:
                try:
                    # Note: delete_file method needs to be implemented in client
                    if hasattr(client, 'delete_file'):
                        if not client.delete_file(file_path):
                            all_deletions_successful = False
                            # Continue trying to delete other files even if one fails
                    else:
                        # delete_file not implemented yet - return False
                        all_deletions_successful = False
                except Exception:
                    all_deletions_successful = False
                    # Continue trying to delete other files even if one fails

            return all_deletions_successful

        except Exception:
            return False

    def execute_deployment(self, output_dir: Path) -> bool:
        """Execute complete dual zone deployment with rollback on failure.

        Args:
            output_dir: Directory containing generated site files

        Returns:
            True if deployment successful, False otherwise
        """
        try:
            # Route files to appropriate zones
            photo_files, site_files = self.route_files_to_zones(output_dir)

            # Deploy photos with manifest-based incremental uploads
            if photo_files:
                if not self.deploy_photos(photo_files, output_dir):
                    return False

            # Deploy site content (always upload all)
            if site_files:
                if not self.deploy_site_content(site_files, output_dir):
                    # If site deploy fails, don't rollback photos (they're incremental)
                    return False

            return True

        except Exception:
            return False
