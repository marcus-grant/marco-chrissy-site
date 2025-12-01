"""Integration tests for image processor workflow."""

from pathlib import Path

from PIL import Image


class TestImageProcessorIntegration:
    """Integration tests for end-to-end thumbnail generation workflow."""

    def test_processor_generates_webp_thumbnails_from_photo_collection(self, tmp_path):
        """E2E: Photo files + metadata → 400x400 WebP thumbnails.

        This test drives the implementation of the entire processor module
        by defining the expected end-to-end workflow from source images
        to optimized thumbnails.
        """
        # Arrange: Create mock source photos (different sizes, formats)
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        # Create test images with different sizes and formats
        photos_metadata = []

        # Photo 1: Landscape JPEG (800x600)
        photo1_path = source_dir / "wedding-001.jpg"
        img1 = Image.new("RGB", (800, 600), color="red")
        img1.save(photo1_path, "JPEG")
        mtime1 = photo1_path.stat().st_mtime

        photos_metadata.append(
            {
                "source_path": str(photo1_path),
                "dest_path": "wedding-001.jpg",
                "hash": "abc123",
                "size_bytes": photo1_path.stat().st_size,
                "mtime": mtime1,
            }
        )

        # Photo 2: Portrait PNG (600x800)
        photo2_path = source_dir / "wedding-002.png"
        img2 = Image.new("RGB", (600, 800), color="blue")
        img2.save(photo2_path, "PNG")
        mtime2 = photo2_path.stat().st_mtime

        photos_metadata.append(
            {
                "source_path": str(photo2_path),
                "dest_path": "wedding-002.jpg",
                "hash": "def456",
                "size_bytes": photo2_path.stat().st_size,
                "mtime": mtime2,
            }
        )

        # Photo 3: Square JPEG (1000x1000)
        photo3_path = source_dir / "wedding-003.jpg"
        img3 = Image.new("RGB", (1000, 1000), color="green")
        img3.save(photo3_path, "JPEG")
        mtime3 = photo3_path.stat().st_mtime

        photos_metadata.append(
            {
                "source_path": str(photo3_path),
                "dest_path": "wedding-003.jpg",
                "hash": "ghi789",
                "size_bytes": photo3_path.stat().st_size,
                "mtime": mtime3,
            }
        )

        # Create PhotoCollection using serializer models
        from galleria.serializer.models import Photo, PhotoCollection

        photos = [Photo(**metadata) for metadata in photos_metadata]
        collection = PhotoCollection(
            name="wedding",
            description="Wedding photos",
            photos=photos,
        )

        # Setup output directory
        output_dir = tmp_path / "thumbnails"
        output_dir.mkdir()

        # Act: Process images to generate thumbnails
        from galleria.processor.image import ImageProcessor

        processor = ImageProcessor()
        results = processor.process_collection(collection, output_dir)

        # Assert: Thumbnails generated with correct properties
        assert len(results) == 3

        # Check each thumbnail
        for i, photo in enumerate(collection.photos):
            # Extract filename from dest_path (without extension)
            filename_base = Path(photo.dest_path).stem
            thumb_path = output_dir / f"{filename_base}.webp"

            assert thumb_path.exists(), f"Thumbnail not created: {thumb_path}"

            # Verify thumbnail is 400x400
            thumb_img = Image.open(thumb_path)
            assert thumb_img.size == (400, 400), (
                f"Expected 400x400, got {thumb_img.size}"
            )
            assert thumb_img.format == "WEBP", (
                f"Expected WEBP format, got {thumb_img.format}"
            )

            # Verify result includes path
            assert results[i]["thumbnail_path"] == str(thumb_path)
            assert results[i]["source_path"] == photo.source_path

    def test_processor_uses_naive_caching_to_skip_existing_thumbnails(self, tmp_path):
        """E2E: Cached thumbnails → Skip processing if source unchanged.

        Tests the naive caching strategy: if thumbnail exists and source file
        mtime is older than thumbnail mtime, skip processing.
        """
        # Arrange: Create source photo
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        output_dir = tmp_path / "thumbnails"
        output_dir.mkdir()

        photo_path = source_dir / "photo.jpg"
        img = Image.new("RGB", (800, 600), color="red")
        img.save(photo_path, "JPEG")

        from galleria.serializer.models import Photo, PhotoCollection

        photo = Photo(
            source_path=str(photo_path),
            dest_path="photo.jpg",
            hash="abc123",
            size_bytes=photo_path.stat().st_size,
            mtime=photo_path.stat().st_mtime,
        )
        collection = PhotoCollection(name="test", photos=[photo])

        # Process once to create thumbnail
        from galleria.processor.image import ImageProcessor

        processor = ImageProcessor()
        results1 = processor.process_collection(collection, output_dir)

        # Get thumbnail mtime
        thumb_path = Path(results1[0]["thumbnail_path"])
        assert thumb_path.exists()
        original_mtime = thumb_path.stat().st_mtime

        # Act: Process again without changing source
        results2 = processor.process_collection(collection, output_dir)

        # Assert: Thumbnail was skipped (cached)
        assert results2[0]["cached"] is True
        assert thumb_path.stat().st_mtime == original_mtime  # Not regenerated

        # Modify source file (touch to update mtime)
        import time

        time.sleep(0.01)  # Ensure mtime difference
        photo_path.touch()

        # Update photo metadata
        photo.mtime = photo_path.stat().st_mtime

        # Act: Process again with modified source
        results3 = processor.process_collection(collection, output_dir)

        # Assert: Thumbnail was regenerated
        assert results3[0]["cached"] is False
        assert thumb_path.stat().st_mtime > original_mtime  # Regenerated

    def test_processor_handles_corrupted_images_gracefully(self, tmp_path):
        """E2E: Corrupted image → Clear error, continue processing others."""
        # Arrange: Create one good image and one corrupted file
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        output_dir = tmp_path / "thumbnails"
        output_dir.mkdir()

        # Good image
        good_path = source_dir / "good.jpg"
        img = Image.new("RGB", (800, 600), color="green")
        img.save(good_path, "JPEG")

        # Corrupted image (invalid data)
        bad_path = source_dir / "bad.jpg"
        bad_path.write_text("This is not a valid image file")

        from galleria.serializer.models import Photo, PhotoCollection

        photos = [
            Photo(
                source_path=str(good_path),
                dest_path="good.jpg",
                hash="good123",
                size_bytes=good_path.stat().st_size,
                mtime=good_path.stat().st_mtime,
            ),
            Photo(
                source_path=str(bad_path),
                dest_path="bad.jpg",
                hash="bad456",
                size_bytes=bad_path.stat().st_size,
                mtime=bad_path.stat().st_mtime,
            ),
        ]
        collection = PhotoCollection(name="mixed", photos=photos)

        # Act: Process collection with error
        from galleria.processor.image import ImageProcessor

        processor = ImageProcessor()
        results = processor.process_collection(collection, output_dir)

        # Assert: Good image processed, bad image has error
        assert len(results) == 2

        # First result should be success
        assert results[0]["source_path"] == str(good_path)
        assert "error" not in results[0]
        assert Path(results[0]["thumbnail_path"]).exists()

        # Second result should have error
        assert results[1]["source_path"] == str(bad_path)
        assert "error" in results[1]
        assert "thumbnail_path" not in results[1]

    def test_processor_reports_progress_for_large_collections(self, tmp_path):
        """E2E: Multiple images → Progress callbacks during processing."""
        # Arrange: Create multiple images
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        output_dir = tmp_path / "thumbnails"
        output_dir.mkdir()

        photos = []
        for i in range(5):
            photo_path = source_dir / f"photo-{i:03d}.jpg"
            img = Image.new("RGB", (800, 600), color="red")
            img.save(photo_path, "JPEG")

            from galleria.serializer.models import Photo

            photos.append(
                Photo(
                    source_path=str(photo_path),
                    dest_path=f"photo-{i:03d}.jpg",
                    hash=f"hash{i}",
                    size_bytes=photo_path.stat().st_size,
                    mtime=photo_path.stat().st_mtime,
                )
            )

        from galleria.serializer.models import PhotoCollection

        collection = PhotoCollection(name="progress", photos=photos)

        # Track progress callbacks
        progress_reports = []

        def progress_callback(current, total, photo_path):
            progress_reports.append(
                {"current": current, "total": total, "path": photo_path}
            )

        # Act: Process with progress callback
        from galleria.processor.image import ImageProcessor

        processor = ImageProcessor()
        processor.process_collection(
            collection, output_dir, progress_callback=progress_callback
        )

        # Assert: Progress reported for each photo
        assert len(progress_reports) == 5
        assert progress_reports[0]["current"] == 1
        assert progress_reports[0]["total"] == 5
        assert progress_reports[4]["current"] == 5
        assert progress_reports[4]["total"] == 5
