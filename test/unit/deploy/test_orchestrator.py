"""Unit tests for deploy orchestrator functionality."""

from pathlib import Path
from unittest.mock import Mock

from deploy.orchestrator import DeployOrchestrator


class TestDeployOrchestrator:
    """Test deploy orchestrator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_bunnynet_client = Mock()
        self.mock_manifest_comparator = Mock()
        self.orchestrator = DeployOrchestrator(
            self.mock_bunnynet_client,
            self.mock_manifest_comparator,
            photo_zone_name="test-photos",
            site_zone_name="test-site"
        )

    def test_route_files_to_zones_separates_photos_and_site(self, temp_filesystem, file_factory):
        """Test file routing separates photos from site content."""
        # Create output directory structure
        output_dir = temp_filesystem / "output"

        # Create photo files (should go to photo zone)
        file_factory(output_dir / "pics" / "full" / "photo1.jpg", content="photo1")
        file_factory(output_dir / "pics" / "full" / "photo2.jpg", content="photo2")
        file_factory(output_dir / "pics" / "thumbs" / "photo1.webp", content="thumb1")

        # Create site files (should go to site zone)
        file_factory(output_dir / "index.html", content="<html>index</html>")
        file_factory(output_dir / "galleries" / "wedding" / "page_1.html", content="<html>gallery</html>")
        file_factory(output_dir / "static" / "style.css", content="body { margin: 0; }")

        # Execute file routing
        photo_files, site_files = self.orchestrator.route_files_to_zones(output_dir)

        # Verify photo files are correctly identified
        photo_paths = {f.relative_to(output_dir) for f in photo_files}
        expected_photo_paths = {
            Path("pics/full/photo1.jpg"),
            Path("pics/full/photo2.jpg"),
            Path("pics/thumbs/photo1.webp")
        }
        assert photo_paths == expected_photo_paths

        # Verify site files are correctly identified
        site_paths = {f.relative_to(output_dir) for f in site_files}
        expected_site_paths = {
            Path("index.html"),
            Path("galleries/wedding/page_1.html"),
            Path("static/style.css")
        }
        assert site_paths == expected_site_paths

    def test_deploy_photos_uses_manifest_comparison(self, temp_filesystem, file_factory):
        """Test photo deployment uses manifest comparison for incremental uploads."""
        # Create output directory with photo files
        output_dir = temp_filesystem / "output"
        photo_file1 = file_factory(output_dir / "pics" / "full" / "photo1.jpg", content="photo1 content")
        photo_file2 = file_factory(output_dir / "pics" / "full" / "photo2.jpg", content="photo2 content")
        photo_files = [photo_file1, photo_file2]

        # Mock manifest comparison - simulate photo1 needs upload, photo2 unchanged
        # Note: manifest paths are relative to pics directory, not including "pics/"
        local_manifest = {"full/photo1.jpg": "hash1", "full/photo2.jpg": "hash2"}
        remote_manifest = {"full/photo2.jpg": "hash2"}  # photo2 unchanged
        files_to_upload = {"full/photo1.jpg"}  # Only photo1 needs upload

        self.mock_manifest_comparator.generate_local_manifest.return_value = local_manifest
        self.mock_manifest_comparator.compare_manifests.return_value = files_to_upload
        self.mock_bunnynet_client.upload_file.return_value = True
        self.mock_bunnynet_client.download_manifest.return_value = b'{"full/photo2.jpg": "hash2"}'
        self.mock_manifest_comparator.load_manifest_from_json.return_value = remote_manifest
        self.mock_manifest_comparator.save_manifest_to_json.return_value = b'{"full/photo1.jpg": "hash1", "full/photo2.jpg": "hash2"}'

        # Execute photo deployment
        result = self.orchestrator.deploy_photos(photo_files, output_dir)

        # Verify manifest comparison was used
        self.mock_manifest_comparator.generate_local_manifest.assert_called_once_with(output_dir / "pics")
        self.mock_bunnynet_client.download_manifest.assert_called_once_with("manifest.json")
        self.mock_manifest_comparator.compare_manifests.assert_called_once_with(local_manifest, remote_manifest)

        # Verify only photo1 was uploaded (incremental upload) + manifest
        expected_upload_calls = 2  # photo1 + manifest
        assert self.mock_bunnynet_client.upload_file.call_count == expected_upload_calls

        # Verify photo1 was uploaded with correct signature
        self.mock_bunnynet_client.upload_file.assert_any_call(
            photo_file1,  # local_path
            "full/photo1.jpg",  # remote_path (relative to pics dir)
            "test-photos"  # zone_name
        )

        # Verify manifest was uploaded with correct signature
        # Note: manifest file is created in pics directory during upload
        manifest_path = output_dir / "pics" / "manifest.json"
        self.mock_bunnynet_client.upload_file.assert_any_call(
            manifest_path,  # local_path
            "manifest.json",  # remote_path
            "test-photos"  # zone_name
        )

        assert result is True

    def test_deploy_site_content_uploads_all_files(self, temp_filesystem, file_factory):
        """Test site content deployment uploads all non-photo files."""
        # Create output directory with site files
        output_dir = temp_filesystem / "output"
        index_file = file_factory(output_dir / "index.html", content="<html>Home</html>")
        gallery_file = file_factory(output_dir / "galleries" / "wedding" / "page_1.html", content="<html>Gallery</html>")
        css_file = file_factory(output_dir / "static" / "style.css", content="body { margin: 0; }")
        site_files = [index_file, gallery_file, css_file]

        # Mock successful uploads
        self.mock_bunnynet_client.upload_file.return_value = True

        # Execute site content deployment
        result = self.orchestrator.deploy_site_content(site_files, output_dir)

        # Verify all site files were uploaded (no manifest comparison for site content)
        expected_upload_calls = 3  # All 3 site files
        assert self.mock_bunnynet_client.upload_file.call_count == expected_upload_calls

        # Verify correct file paths and zone names
        self.mock_bunnynet_client.upload_file.assert_any_call(
            index_file,  # local_path
            "index.html",  # remote_path
            "test-site"  # zone_name
        )
        self.mock_bunnynet_client.upload_file.assert_any_call(
            gallery_file,  # local_path
            "galleries/wedding/page_1.html",  # remote_path
            "test-site"  # zone_name
        )
        self.mock_bunnynet_client.upload_file.assert_any_call(
            css_file,  # local_path
            "static/style.css",  # remote_path
            "test-site"  # zone_name
        )

        assert result is True

    def test_rollback_deployment_removes_uploaded_files(self):
        """Test rollback removes files that were uploaded during failed deployment."""
        deployed_files = ["full/photo1.jpg", "full/photo2.jpg"]

        # Mock successful file deletions
        self.mock_bunnynet_client.delete_file.return_value = True

        # Execute rollback
        result = self.orchestrator.rollback_deployment(deployed_files, "photo")

        # Verify all deployed files were deleted
        expected_delete_calls = 2
        assert self.mock_bunnynet_client.delete_file.call_count == expected_delete_calls

        # Verify correct files were deleted
        self.mock_bunnynet_client.delete_file.assert_any_call("full/photo1.jpg")
        self.mock_bunnynet_client.delete_file.assert_any_call("full/photo2.jpg")

        assert result is True

    def test_rollback_deployment_handles_deletion_failures(self):
        """Test rollback handles individual file deletion failures gracefully."""
        deployed_files = ["full/photo1.jpg", "full/photo2.jpg"]

        # Mock mixed deletion results - first succeeds, second fails
        self.mock_bunnynet_client.delete_file.side_effect = [True, False]

        # Execute rollback
        result = self.orchestrator.rollback_deployment(deployed_files, "photo")

        # Should continue trying to delete all files even if some fail
        assert self.mock_bunnynet_client.delete_file.call_count == 2

        # Should return False if any deletions failed
        assert result is False

    def test_orchestrator_accepts_zone_names_and_passes_to_upload_calls(self, temp_filesystem, file_factory):
        """Test orchestrator accepts zone names and passes them to upload_file calls."""
        # Setup orchestrator with zone names
        photo_zone_name = "marco-crissy-site-pics"
        site_zone_name = "marco-crissy-site"
        orchestrator = DeployOrchestrator(
            self.mock_bunnynet_client,
            self.mock_manifest_comparator,
            photo_zone_name=photo_zone_name,
            site_zone_name=site_zone_name
        )

        # Create output directory with photo and site files
        output_dir = temp_filesystem / "output"
        photo_file = file_factory(output_dir / "pics" / "full" / "photo1.jpg", content="photo1")
        site_file = file_factory(output_dir / "index.html", content="<html>home</html>")

        # Mock successful uploads
        self.mock_bunnynet_client.upload_file.return_value = True

        # Mock manifest operations for photo deployment
        local_manifest = {"full/photo1.jpg": "hash1"}
        self.mock_manifest_comparator.generate_local_manifest.return_value = local_manifest
        self.mock_manifest_comparator.compare_manifests.return_value = {"full/photo1.jpg"}
        self.mock_bunnynet_client.download_manifest.return_value = b'{}'
        self.mock_manifest_comparator.load_manifest_from_json.return_value = {}
        self.mock_manifest_comparator.save_manifest_to_json.return_value = b'{"full/photo1.jpg": "hash1"}'

        # Execute deployment
        result = orchestrator.execute_deployment(output_dir)

        # Verify photo upload calls include zone_name
        self.mock_bunnynet_client.upload_file.assert_any_call(
            photo_file,  # local_path
            "full/photo1.jpg",  # remote_path
            photo_zone_name  # zone_name
        )

        # Verify photo manifest upload includes zone_name
        self.mock_bunnynet_client.upload_file.assert_any_call(
            output_dir / "pics" / "manifest.json",  # local_path (will need to be created)
            "manifest.json",  # remote_path
            photo_zone_name  # zone_name
        )

        # Verify site file upload includes zone_name
        self.mock_bunnynet_client.upload_file.assert_any_call(
            site_file,  # local_path
            "index.html",  # remote_path
            site_zone_name  # zone_name
        )

        assert result is True

    def test_execute_deployment_coordinates_dual_zone_strategy(self, temp_filesystem, file_factory):
        """Test execute_deployment coordinates photo and site deployment."""
        # Create output directory with both photos and site files
        output_dir = temp_filesystem / "output"

        # Create photo files
        file_factory(output_dir / "pics" / "full" / "photo1.jpg", content="photo1")
        file_factory(output_dir / "pics" / "thumbs" / "thumb1.webp", content="thumb1")

        # Create site files
        file_factory(output_dir / "index.html", content="<html>home</html>")
        file_factory(output_dir / "static" / "style.css", content="body{}")

        # Mock successful deployments
        self.orchestrator.deploy_photos = Mock(return_value=True)
        self.orchestrator.deploy_site_content = Mock(return_value=True)
        self.orchestrator.route_files_to_zones = Mock(return_value=(
            [output_dir / "pics" / "full" / "photo1.jpg", output_dir / "pics" / "thumbs" / "thumb1.webp"],
            [output_dir / "index.html", output_dir / "static" / "style.css"]
        ))

        # Execute full deployment
        result = self.orchestrator.execute_deployment(output_dir)

        # Verify routing was called
        self.orchestrator.route_files_to_zones.assert_called_once_with(output_dir)

        # Verify both deployment methods were called
        self.orchestrator.deploy_photos.assert_called_once()
        self.orchestrator.deploy_site_content.assert_called_once()

        assert result is True

    def test_execute_deployment_handles_photo_deploy_failure(self, temp_filesystem, file_factory):
        """Test execute_deployment stops if photo deployment fails."""
        output_dir = temp_filesystem / "output"

        # Create files
        file_factory(output_dir / "pics" / "full" / "photo1.jpg", content="photo1")
        file_factory(output_dir / "index.html", content="<html>home</html>")

        # Mock photo deployment failure
        self.orchestrator.deploy_photos = Mock(return_value=False)
        self.orchestrator.deploy_site_content = Mock(return_value=True)
        self.orchestrator.route_files_to_zones = Mock(return_value=(
            [output_dir / "pics" / "full" / "photo1.jpg"],
            [output_dir / "index.html"]
        ))

        # Execute deployment
        result = self.orchestrator.execute_deployment(output_dir)

        # Should stop on photo failure and not attempt site deployment
        self.orchestrator.deploy_photos.assert_called_once()
        self.orchestrator.deploy_site_content.assert_not_called()

        assert result is False
