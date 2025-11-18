"""Unit tests for ImageProcessor."""


import pytest
from PIL import Image


class TestImageProcessorProcessImage:
    """Unit tests for ImageProcessor.process_image method."""

    def test_process_image_converts_jpeg_to_webp(self, tmp_path):
        """Process single JPEG → WebP thumbnail."""
        # Arrange: Create test JPEG
        source_path = tmp_path / "source.jpg"
        img = Image.new("RGB", (800, 600), color="red")
        img.save(source_path, "JPEG")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Act: Process image
        from galleria.processor.image import ImageProcessor

        processor = ImageProcessor()
        result_path = processor.process_image(source_path, output_dir, size=400)

        # Assert: WebP created
        assert result_path.exists()
        assert result_path.suffix == ".webp"

        # Verify image properties
        result_img = Image.open(result_path)
        assert result_img.format == "WEBP"
        assert result_img.size == (400, 400)

    def test_process_image_converts_png_to_webp(self, tmp_path):
        """Process PNG → WebP thumbnail."""
        # Arrange: Create test PNG
        source_path = tmp_path / "source.png"
        img = Image.new("RGB", (600, 800), color="blue")
        img.save(source_path, "PNG")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Act: Process image
        from galleria.processor.image import ImageProcessor

        processor = ImageProcessor()
        result_path = processor.process_image(source_path, output_dir, size=400)

        # Assert: WebP created
        assert result_path.exists()
        assert result_path.suffix == ".webp"
        result_img = Image.open(result_path)
        assert result_img.format == "WEBP"
        assert result_img.size == (400, 400)

    def test_process_image_uses_center_crop_for_landscape(self, tmp_path):
        """Landscape image → Center crop to square."""
        # Arrange: Create landscape image with distinct colors in regions
        source_path = tmp_path / "landscape.jpg"
        img = Image.new("RGB", (1000, 600), color="red")
        # Add blue stripe in center to verify center crop
        from PIL import ImageDraw

        draw = ImageDraw.Draw(img)
        draw.rectangle([400, 0, 600, 600], fill="blue")
        img.save(source_path, "JPEG")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Act: Process with center crop
        from galleria.processor.image import ImageProcessor

        processor = ImageProcessor()
        result_path = processor.process_image(source_path, output_dir, size=400)

        # Assert: Center is preserved (blue should be visible)
        result_img = Image.open(result_path)
        # Check center pixel should be blue
        center_pixel = result_img.getpixel((200, 200))
        # Blue pixel in RGB
        assert center_pixel[2] > 200  # High blue value

    def test_process_image_uses_center_crop_for_portrait(self, tmp_path):
        """Portrait image → Center crop to square."""
        # Arrange: Create portrait image with distinct colors
        source_path = tmp_path / "portrait.jpg"
        img = Image.new("RGB", (600, 1000), color="red")
        # Add blue stripe in center
        from PIL import ImageDraw

        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 400, 600, 600], fill="blue")
        img.save(source_path, "JPEG")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Act: Process with center crop
        from galleria.processor.image import ImageProcessor

        processor = ImageProcessor()
        result_path = processor.process_image(source_path, output_dir, size=400)

        # Assert: Center is preserved
        result_img = Image.open(result_path)
        center_pixel = result_img.getpixel((200, 200))
        assert center_pixel[2] > 200  # High blue value

    def test_process_image_handles_square_image(self, tmp_path):
        """Square image → No cropping needed, just resize."""
        # Arrange: Create square image
        source_path = tmp_path / "square.jpg"
        img = Image.new("RGB", (1000, 1000), color="green")
        img.save(source_path, "JPEG")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Act: Process square image
        from galleria.processor.image import ImageProcessor

        processor = ImageProcessor()
        result_path = processor.process_image(source_path, output_dir, size=400)

        # Assert: Resized to 400x400
        result_img = Image.open(result_path)
        assert result_img.size == (400, 400)

    def test_process_image_preserves_filename_stem(self, tmp_path):
        """Output filename should preserve source stem with .webp extension."""
        # Arrange
        source_path = tmp_path / "my-photo-name.jpg"
        img = Image.new("RGB", (800, 600), color="red")
        img.save(source_path, "JPEG")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Act
        from galleria.processor.image import ImageProcessor

        processor = ImageProcessor()
        result_path = processor.process_image(source_path, output_dir)

        # Assert: Filename stem preserved
        assert result_path.name == "my-photo-name.webp"

    def test_process_image_uses_custom_size(self, tmp_path):
        """Process with custom thumbnail size."""
        # Arrange
        source_path = tmp_path / "photo.jpg"
        img = Image.new("RGB", (1000, 1000), color="red")
        img.save(source_path, "JPEG")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Act: Process with custom size
        from galleria.processor.image import ImageProcessor

        processor = ImageProcessor()
        result_path = processor.process_image(source_path, output_dir, size=200)

        # Assert: Custom size used
        result_img = Image.open(result_path)
        assert result_img.size == (200, 200)

    def test_process_image_applies_quality_setting(self, tmp_path):
        """WebP quality setting affects file size."""
        # Arrange
        source_path = tmp_path / "photo.jpg"
        img = Image.new("RGB", (800, 600), color="red")
        img.save(source_path, "JPEG")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Act: Process with different quality settings
        from galleria.processor.image import ImageProcessor

        processor = ImageProcessor()

        # High quality
        path_high = processor.process_image(source_path, output_dir, quality=95)
        size_high = path_high.stat().st_size

        # Low quality (new output dir to avoid name conflict)
        output_dir2 = tmp_path / "output2"
        output_dir2.mkdir()
        path_low = processor.process_image(source_path, output_dir2, quality=60)
        size_low = path_low.stat().st_size

        # Assert: Higher quality = larger file
        assert size_high > size_low

    def test_process_image_raises_error_for_invalid_file(self, tmp_path):
        """Invalid image file → Raise clear error."""
        # Arrange: Create invalid image file
        source_path = tmp_path / "invalid.jpg"
        source_path.write_text("Not an image")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Act & Assert: Should raise error
        from galleria.processor.image import ImageProcessingError, ImageProcessor

        processor = ImageProcessor()
        with pytest.raises(ImageProcessingError) as exc_info:
            processor.process_image(source_path, output_dir)

        assert "invalid" in str(exc_info.value).lower() or "cannot" in str(exc_info.value).lower()

    def test_process_image_raises_error_for_missing_file(self, tmp_path):
        """Missing source file → Raise clear error."""
        # Arrange
        source_path = tmp_path / "missing.jpg"
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Act & Assert
        from galleria.processor.image import ImageProcessingError, ImageProcessor

        processor = ImageProcessor()
        with pytest.raises(ImageProcessingError) as exc_info:
            processor.process_image(source_path, output_dir)

        assert "not found" in str(exc_info.value).lower() or "does not exist" in str(exc_info.value).lower()


class TestImageProcessorCaching:
    """Unit tests for thumbnail caching logic."""

    def test_should_process_returns_true_when_thumbnail_missing(self, tmp_path):
        """No thumbnail → Should process."""
        # Arrange
        source_path = tmp_path / "photo.jpg"
        img = Image.new("RGB", (800, 600), color="red")
        img.save(source_path, "JPEG")

        thumb_path = tmp_path / "photo.webp"
        # thumb_path does not exist

        # Act
        from galleria.processor.image import ImageProcessor

        processor = ImageProcessor()
        should_process = processor.should_process(source_path, thumb_path)

        # Assert
        assert should_process is True

    def test_should_process_returns_false_when_thumbnail_newer(self, tmp_path):
        """Thumbnail newer than source → Should not process."""
        # Arrange: Create source
        source_path = tmp_path / "photo.jpg"
        img = Image.new("RGB", (800, 600), color="red")
        img.save(source_path, "JPEG")

        # Create thumbnail
        thumb_path = tmp_path / "photo.webp"
        img.save(thumb_path, "WEBP")

        # Touch thumbnail to make it newer
        import time

        time.sleep(0.01)
        thumb_path.touch()

        # Act
        from galleria.processor.image import ImageProcessor

        processor = ImageProcessor()
        should_process = processor.should_process(source_path, thumb_path)

        # Assert: Should not reprocess
        assert should_process is False

    def test_should_process_returns_true_when_source_modified(self, tmp_path):
        """Source modified after thumbnail → Should reprocess."""
        # Arrange: Create thumbnail first
        thumb_path = tmp_path / "photo.webp"
        img = Image.new("RGB", (400, 400), color="red")
        img.save(thumb_path, "WEBP")

        # Create source after thumbnail
        import time

        time.sleep(0.01)
        source_path = tmp_path / "photo.jpg"
        img2 = Image.new("RGB", (800, 600), color="blue")
        img2.save(source_path, "JPEG")

        # Act
        from galleria.processor.image import ImageProcessor

        processor = ImageProcessor()
        should_process = processor.should_process(source_path, thumb_path)

        # Assert: Should reprocess
        assert should_process is True
